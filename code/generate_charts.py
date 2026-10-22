# -*- coding: utf-8 -*-
"""
generate_charts.py
基于清洗后的招聘数据生成分析图表，输出到 images/ 目录。
对应赛题「任务④：数据可视化展示」。
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 无界面环境使用 Agg 后端，避免依赖 Tk 图形界面
import matplotlib.pyplot as plt

# 中文字体设置（Windows 常用字体，避免中文乱码）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 路径定位（脚本位于 code/ 目录，项目根在其上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', '招聘数据_清洗后.csv')
OUT_DIR = os.path.join(BASE_DIR, 'images')
os.makedirs(OUT_DIR, exist_ok=True)

# 读取数据
df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
print(f"加载数据：{len(df):,} 条")

# 岗位分类的无效值列表（与 data_cleaning.py 口径一致）
INVALID = ['全职', '-', '其他', '不限', 'nan', 'NaN', '', 'nan']


def save(fig, name):
    """保存图表到 images/ 目录"""
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"已保存：{path}")


# ========== 图1：招聘量最多的10个行业 ==========
top_industry = df['上市公司行业'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
top_industry.sort_values().plot(kind='barh', ax=ax, color='steelblue')
ax.set_xlabel('招聘数量')
ax.set_title('招聘量最多的 10 个行业')
save(fig, '行业招聘量Top10.png')

# ========== 图2：招聘量最多的10个城市 ==========
top_city = df['工作城市'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
top_city.sort_values().plot(kind='barh', ax=ax, color='coral')
ax.set_xlabel('招聘数量')
ax.set_title('招聘量最多的 10 个城市')
save(fig, '城市招聘量Top10.png')

# ========== 图3：学历要求分布 ==========
edu_counts = df['学历_简化'].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
edu_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
ax.set_ylabel('')
ax.set_title('学历要求分布')
save(fig, '学历要求分布.png')

# ========== 图4：平均薪资最高的10个行业 ==========
# 过滤样本量过小的行业，保证均值可靠
valid_ind = df.groupby('上市公司行业').size()
industries = valid_ind[valid_ind >= 30].index
df_valid = df[df['上市公司行业'].isin(industries)]
salary_top = df_valid.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 6))
salary_top.sort_values().plot(kind='barh', ax=ax, color='green')
ax.set_xlabel('平均月薪（元）')
ax.set_title('平均薪资最高的 10 个行业')
save(fig, '高薪行业Top10.png')

# ========== 图5：招聘岗位需求 Top10 ==========
job_col = '岗位分类'
df_job = df[~df[job_col].isin(INVALID) & df[job_col].notna() & (df[job_col] != '')]
job_top = df_job[job_col].value_counts().head(10)
fig, ax = plt.subplots(figsize=(12, 6))
job_top.plot(kind='bar', ax=ax, color='purple')
ax.set_xlabel('岗位类别')
ax.set_ylabel('招聘数量')
ax.set_title('招聘岗位需求 Top10')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
save(fig, '岗位需求Top10.png')

# ========== 图6：薪资分布直方图 ==========
fig, ax = plt.subplots(figsize=(12, 5))
df['平均月薪'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.set_xlabel('平均月薪（元）')
ax.set_ylabel('频次')
ax.set_title('薪资分布直方图')
save(fig, '薪资分布直方图.png')

print("全部图表生成完毕。")
