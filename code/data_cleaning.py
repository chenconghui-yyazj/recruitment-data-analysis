import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# ========== 1. 读取数据并探测字段 ==========
print("正在分块读取数据...")
chunk_size = 100000
sample_frac = 0.05  # 5%采样
chunks = []
total_rows = 0

# 先读取第一块查看字段名
first_chunk = pd.read_csv('上市公司招聘大数据2014-2026.3.csv',
                          encoding='utf-8',
                          nrows=5)
print("\n=== 数据字段列表 ===")
for i, col in enumerate(first_chunk.columns):
    print(f"{i + 1}. {col}")

for chunk in pd.read_csv('上市公司招聘大数据2014-2026.3.csv',
                         encoding='utf-8',
                         low_memory=False,
                         chunksize=chunk_size):
    sampled = chunk.sample(frac=sample_frac, random_state=42)
    chunks.append(sampled)
    total_rows += len(chunk)
    print(f"已处理 {total_rows:,} 行...", end='\r')

df = pd.concat(chunks, ignore_index=True)
print(f"\n原始数据约 {total_rows:,} 行，采样后 {len(df):,} 行")

# ========== 2. 字段标准化（避免重复）==========
print("\n=== 字段映射与标准化 ===")

# 保留原始字段名的副本
original_columns = df.columns.tolist()

# 创建新的字段映射（避免重名）
field_mapping = {}

# 时间字段
if '招聘发布日期' in df.columns:
    field_mapping['招聘发布日期'] = '发布时间'
    print(f"使用时间字段: 招聘发布日期 -> 发布时间")
elif '招聘结束日期' in df.columns:
    field_mapping['招聘结束日期'] = '发布时间'
    print(f"使用时间字段: 招聘结束日期 -> 发布时间")

# 行业字段
if '上市公司行业' in df.columns:
    print(f"使用行业字段: 上市公司行业")

# 城市字段
if '工作城市' in df.columns:
    print(f"使用城市字段: 工作城市")

# 学历字段
if '学历要求' in df.columns:
    print(f"使用学历字段: 学历要求")

# 岗位字段 - 优先使用初级分类，其次是招聘岗位
if '初级分类' in df.columns and '初级分类' not in field_mapping.values():
    field_mapping['初级分类'] = '岗位分类'
    print(f"使用岗位字段: 初级分类 -> 岗位分类")
elif '招聘岗位' in df.columns:
    field_mapping['招聘岗位'] = '岗位分类'
    print(f"使用岗位字段: 招聘岗位 -> 岗位分类")

# 薪资字段
if '最低月薪' in df.columns and '最高月薪' in df.columns:
    print(f"使用薪资字段: 最低月薪、最高月薪")

# 应用字段重命名（避免重复）
df = df.rename(columns=field_mapping)

print(f"\n标准化后的字段: {df.columns.tolist()}")


# ========== 3. 薪资转换 ==========
def convert_salary(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val) if 1000 <= val <= 500000 else None
    if isinstance(val, str):
        val = val.replace(',', '').replace('，', '').replace('元', '').replace('k', '000').strip()
        try:
            num = float(val)
            return num if 1000 <= num <= 500000 else None
        except:
            return None
    return None


df['最低月薪_数值'] = df['最低月薪'].apply(convert_salary)
df['最高月薪_数值'] = df['最高月薪'].apply(convert_salary)

# ========== 4. 数据清洗 ==========
print("\n=== 数据清洗 ===")
initial_count = len(df)

# 移除薪资无效记录
df_clean = df.dropna(subset=['最低月薪_数值', '最高月薪_数值'])
df_clean = df_clean[(df_clean['最低月薪_数值'] > 0) & (df_clean['最高月薪_数值'] > 0)]
df_clean = df_clean[df_clean['最高月薪_数值'] >= df_clean['最低月薪_数值']]

# IQR方法识别薪资异常
Q1 = df_clean['最高月薪_数值'].quantile(0.25)
Q3 = df_clean['最高月薪_数值'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
salary_outliers = df_clean[(df_clean['最高月薪_数值'] < lower_bound) |
                           (df_clean['最高月薪_数值'] > upper_bound)]
print(f"识别出薪资异常记录: {len(salary_outliers)} 条 ({len(salary_outliers) / len(df_clean) * 100:.2f}%)")

# 剔除薪资异常值
df_clean = df_clean[(df_clean['最高月薪_数值'] >= lower_bound) &
                    (df_clean['最高月薪_数值'] <= upper_bound)]

# 移除关键字段缺失值
required_cols = ['学历要求', '上市公司行业', '工作城市']
existing_required = [col for col in required_cols if col in df_clean.columns]
df_clean = df_clean.dropna(subset=existing_required)
df_clean['平均月薪'] = (df_clean['最低月薪_数值'] + df_clean['最高月薪_数值']) / 2

# 移除重复项
df_clean = df_clean.drop_duplicates()

print(f"原始采样数据：{len(df):,} 行")
print(f"清洗后数据：{len(df_clean):,} 行")
print(f"数据保留率：{len(df_clean) / len(df) * 100:.2f}%")

# ========== 5. 时间处理 ==========
print("\n=== 时间处理 ===")

# 检查是否有发布时间字段
if '发布时间' in df_clean.columns:
    df_clean['发布时间'] = pd.to_datetime(df_clean['发布时间'], errors='coerce')
    df_clean = df_clean.dropna(subset=['发布时间'])
    df_clean['年份'] = df_clean['发布时间'].dt.year
    df_clean['月份'] = df_clean['发布时间'].dt.month
    df_clean['年月'] = df_clean['发布时间'].dt.to_period('M')

    # 过滤有效年份
    df_clean = df_clean[(df_clean['年份'] >= 2014) & (df_clean['年份'] <= 2026)]
    print(f"有效年份范围：{df_clean['年份'].min()} - {df_clean['年份'].max()}")
else:
    # 如果没有发布时间，使用招聘发布年份
    if '招聘发布年份' in df_clean.columns:
        df_clean['年份'] = df_clean['招聘发布年份']
        df_clean['月份'] = 1  # 默认月份
        print(f"使用招聘发布年份字段，年份范围：{df_clean['年份'].min()} - {df_clean['年份'].max()}")
    else:
        print("警告：未找到时间字段，将创建模拟时间")
        df_clean['年份'] = 2015
        df_clean['月份'] = 1


# ========== 6. 学历简化 ==========
def simplify_edu(edu):
    if pd.isna(edu):
        return '未知'
    edu_str = str(edu)
    if '博士' in edu_str:
        return '博士'
    elif '硕士' in edu_str:
        return '硕士'
    elif '本科' in edu_str:
        return '本科'
    elif '大专' in edu_str:
        return '大专'
    elif '不限' in edu_str or '无' in edu_str or '不限制' in edu_str:
        return '不限'
    else:
        return '其他'


df_clean['学历_简化'] = df_clean['学历要求'].apply(simplify_edu)

# ========== 7. 统计分析 ==========
print("\n=== 招聘量最多的10个行业 ===")
industry_counts = df_clean['上市公司行业'].value_counts().head(10)
print(industry_counts)

print("\n=== 招聘量最多的10个城市 ===")
city_counts = df_clean['工作城市'].value_counts().head(10)
print(city_counts)

print("\n=== 学历要求分布 ===")
edu_simple = df_clean['学历_简化'].value_counts()
print(edu_simple)

# 修复岗位分类字段问题
print("\n=== 招聘量最多的10个岗位类别 ===")
# 使用正确的岗位字段名
job_field = None
if '岗位分类' in df_clean.columns:
    job_field = '岗位分类'
elif '初级分类' in df_clean.columns:
    job_field = '初级分类'
elif '招聘岗位' in df_clean.columns:
    job_field = '招聘岗位'

if job_field:
    # 过滤无效分类
    invalid_cats = ['全职', '-', '其他', '不限', 'nan', 'NaN']
    df_valid_job = df_clean[~df_clean[job_field].isin(invalid_cats)]
    category_counts = df_valid_job[job_field].value_counts().head(10)
    print(category_counts)
else:
    print("未找到岗位分类字段")
    category_counts = pd.Series()

# 平均薪资最高的10个行业（过滤样本量过小的）
print("\n=== 平均薪资最高的10个行业 ===")
industry_counts_valid = df_clean.groupby('上市公司行业').size()
valid_industries = industry_counts_valid[industry_counts_valid >= 30].index
df_valid = df_clean[df_clean['上市公司行业'].isin(valid_industries)]
industry_salary_valid = df_valid.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
print(industry_salary_valid)

# ========== 8. 热点岗位识别 ==========
print("\n=== 热点岗位识别（增长最快岗位） ===")
if job_field and len(df_clean['年份'].unique()) >= 2:
    invalid_cats = ['全职', '-', '其他', '不限', 'nan', 'NaN']
    df_valid_cat = df_clean[~df_clean[job_field].isin(invalid_cats)]

    years = sorted(df_valid_cat['年份'].unique())
    if len(years) >= 2:
        start_year = years[0]
        end_year = years[-1]

        cat_start = df_valid_cat[df_valid_cat['年份'] == start_year][job_field].value_counts()
        cat_end = df_valid_cat[df_valid_cat['年份'] == end_year][job_field].value_counts()

        common_cats = set(cat_start.index) & set(cat_end.index)
        growth_rates = {}
        for cat in common_cats:
            if cat_start[cat] > 0:
                growth_rates[cat] = (cat_end[cat] - cat_start[cat]) / cat_start[cat] * 100

        if growth_rates:
            growth_df = pd.DataFrame(list(growth_rates.items()), columns=['岗位', '增长率%'])
            growth_df = growth_df.sort_values('增长率%', ascending=False).head(10)
            print(f"\n招聘增长最快的10个岗位（{start_year} → {end_year}）：")
            print(growth_df)
        else:
            print("无法计算岗位增长率")
    else:
        print("年份数据不足，无法计算增长率")
else:
    print("岗位分类字段或年份数据不足")

# ========== 9. 时间趋势分析 ==========
print("\n=== 时间趋势分析 ===")
if '年月' in df_clean.columns and len(df_clean['年月'].unique()) > 1:
    monthly_trend = df_clean.groupby('年月').size()
    print(f"月均招聘量：{monthly_trend.mean():.0f}")
    print(f"招聘高峰期（Top3月份）：")
    print(monthly_trend.sort_values(ascending=False).head(3))

    # 薪资趋势
    if len(df_clean['年份'].unique()) >= 2:
        salary_trend = df_clean.groupby('年份')['平均月薪'].mean()
        if len(salary_trend) >= 2:
            growth_rate = (salary_trend.iloc[-1] / salary_trend.iloc[0] - 1) * 100
            print(f"\n薪资年增长率：{growth_rate:.1f}%")
            print("\n各年度平均薪资：")
            print(salary_trend)
else:
    print("时间数据不足，跳过趋势分析")

# ========== 10. 保存清洗后数据 ==========
# 选择要保存的关键字段
save_columns = ['上市公司行业', '工作城市', '学历要求', '学历_简化', '岗位分类',
                '平均月薪', '最低月薪_数值', '最高月薪_数值', '年份', '月份']
existing_save_cols = [col for col in save_columns if col in df_clean.columns]
if '岗位分类' not in existing_save_cols and job_field:
    existing_save_cols.append(job_field)

df_save = df_clean[existing_save_cols]
df_save.to_csv('招聘数据_清洗后.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ 清洗后数据已保存：招聘数据_清洗后.csv (共{len(df_save)}行，{len(existing_save_cols)}个字段)")

# ========== 11. 生成数据报告 ==========
print("\n" + "=" * 60)
print("数据清洗报告")
print("=" * 60)
print(f"原始数据总行数：{total_rows:,}")
print(f"采样比例：{sample_frac * 100}%")
print(f"采样后行数：{len(df):,}")
print(f"清洗后行数：{len(df_clean):,}")
print(f"数据保留率：{len(df_clean) / len(df) * 100:.2f}%")
print(f"有效年份：{df_clean['年份'].min()} - {df_clean['年份'].max()}")
print(f"覆盖行业数：{df_clean['上市公司行业'].nunique()}")
print(f"覆盖城市数：{df_clean['工作城市'].nunique()}")
if job_field:
    print(f"覆盖岗位数：{df_clean[job_field].nunique()}")
print("=" * 60)

# 保存报告到文件
with open('数据清洗报告.txt', 'w', encoding='utf-8') as f:
    f.write("上市公司招聘数据清洗报告\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"原始数据总行数：{total_rows:,}\n")
    f.write(f"采样比例：{sample_frac * 100}%\n")
    f.write(f"采样后行数：{len(df):,}\n")
    f.write(f"清洗后行数：{len(df_clean):,}\n")
    f.write(f"数据保留率：{len(df_clean) / len(df) * 100:.2f}%\n\n")
    f.write("主要清洗操作：\n")
    f.write("1. 薪资异常值剔除（IQR方法）\n")
    f.write("2. 缺失值删除（行业、城市、学历字段）\n")
    f.write("3. 重复记录删除\n")
    f.write("4. 时间字段解析与过滤\n\n")
    f.write(f"最终数据集包含{len(df_clean):,}条有效招聘记录\n")
    f.write(f"数据时间范围：{df_clean['年份'].min()}年 - {df_clean['年份'].max()}年\n")
    f.write(f"覆盖行业：{df_clean['上市公司行业'].nunique()}个\n")
    f.write(f"覆盖城市：{df_clean['工作城市'].nunique()}个\n")

print("\n✅ 分析完成！")