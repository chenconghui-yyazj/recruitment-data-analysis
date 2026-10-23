# -*- coding: utf-8 -*-
"""
generate_charts.py
Generate analysis charts in BOTH Chinese and English, output into images/zh/ and images/en/.
英文图表：标题、坐标轴、数据类别标签均为英文；中文图表：均为中文。
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 中文字体（用于中文图；英文图含中文字体回退以防万一）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'recruitment_data_cleaned.csv')
OUT_DIR = os.path.join(BASE_DIR, 'images')
INVALID = ['全职', '-', '其他', '不限', 'nan', 'NaN', '', 'nan']

# ===== 类别标签中→英映射（Top 项）=====
IND_EN = {'软件和信息技术服务业':'Software & IT Services','计算机、通信和其他电子设备制造业':'Computer & Electronic Equipment Mfg',
'电气机械和器材制造业':'Electrical Machinery Mfg','医药制造业':'Pharmaceutical Mfg','房地产业':'Real Estate',
'专用设备制造业':'Specialized Equipment Mfg','商务服务业':'Business Services','汽车制造业':'Automobile Mfg',
'货币金融服务':'Monetary Finance','电信、广播电视和卫星传输服务':'Telecom & Satellite Services','体育':'Sports',
'互联网和相关服务':'Internet Services','建筑安装业':'Building Installation','零售业':'Retail'}
CITY_EN = {'北京':'Beijing','上海':'Shanghai','深圳':'Shenzhen','杭州':'Hangzhou','广州':'Guangzhou','成都':'Chengdu','武汉':'Wuhan','南京':'Nanjing'}
EDU_EN = {'本科':'Bachelor','大专':'Associate','不限':'Open','其他':'Other','硕士':'Master','博士':'PhD'}
JOB_EN = {'技术':'Technical','销售/客服/技术支持':'Sales/Customer Support','财务/人力资源/行政':'Finance/HR/Admin',
'制药/医疗':'Pharma/Medical','IT/互联网':'IT/Internet','运营':'Operations','咨询/法律/翻译/商标/专利':'Consulting/Legal/Translation','职能':'Functional'}


def T(mapping, val, lang):
    """translate a category label if lang=='en', else keep original."""
    if lang == 'zh':
        return val
    return mapping.get(val, val)  # 未在映射内的标签保留原文


def make(lang):
    """generate all charts in one language into images/<lang>/"""
    outdir = os.path.join(OUT_DIR, lang)
    os.makedirs(outdir, exist_ok=True)
    df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
    print(f"[{lang}] loaded {len(df):,} records")

    # ---- Chart 1: Top10 industries ----
    c = df['上市公司行业'].value_counts().head(10)
    c.index = [T(IND_EN, x, lang) for x in c.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    c.sort_values().plot(kind='barh', ax=ax, color='steelblue')
    ax.set_xlabel('招聘数量' if lang=='zh' else 'Number of Job Postings')
    ax.set_title('招聘量最多的 10 个行业' if lang=='zh' else 'Top 10 Industries by Job Postings')
    fig.savefig(os.path.join(outdir, 'industry_top10.png'), dpi=150, bbox_inches='tight'); plt.close(fig)

    # ---- Chart 2: Top10 cities ----
    c = df['工作城市'].value_counts().head(10)
    c.index = [T(CITY_EN, x, lang) for x in c.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    c.sort_values().plot(kind='barh', ax=ax, color='coral')
    ax.set_xlabel('招聘数量' if lang=='zh' else 'Number of Job Postings')
    ax.set_title('招聘量最多的 10 个城市' if lang=='zh' else 'Top 10 Cities by Job Postings')
    fig.savefig(os.path.join(outdir, 'city_top10.png'), dpi=150, bbox_inches='tight'); plt.close(fig)

    # ---- Chart 3: Education distribution ----
    c = df['学历_简化'].value_counts()
    c.index = [T(EDU_EN, x, lang) for x in c.index]
    fig, ax = plt.subplots(figsize=(8, 6))
    c.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
    ax.set_ylabel('')
    ax.set_title('学历要求分布' if lang=='zh' else 'Education Requirement Distribution')
    fig.savefig(os.path.join(outdir, 'education_distribution.png'), dpi=150, bbox_inches='tight'); plt.close(fig)

    # ---- Chart 4: Top10 industries by avg salary ----
    vi = df.groupby('上市公司行业').size()
    ind = vi[vi >= 30].index
    dv = df[df['上市公司行业'].isin(ind)]
    c = dv.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
    c.index = [T(IND_EN, x, lang) for x in c.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    c.sort_values().plot(kind='barh', ax=ax, color='green')
    ax.set_xlabel('平均月薪（元）' if lang=='zh' else 'Average Monthly Salary (CNY)')
    ax.set_title('平均薪资最高的 10 个行业' if lang=='zh' else 'Top 10 Industries by Average Salary')
    fig.savefig(os.path.join(outdir, 'salary_top_industries.png'), dpi=150, bbox_inches='tight'); plt.close(fig)

    # ---- Chart 5: Top10 job categories ----
    dj = df[~df['岗位分类'].isin(INVALID) & df['岗位分类'].notna() & (df['岗位分类'] != '')]
    c = dj['岗位分类'].value_counts().head(10)
    c.index = [T(JOB_EN, x, lang) for x in c.index]
    fig, ax = plt.subplots(figsize=(12, 6))
    c.plot(kind='bar', ax=ax, color='purple')
    ax.set_xlabel('岗位类别' if lang=='zh' else 'Job Category')
    ax.set_ylabel('招聘数量' if lang=='zh' else 'Number of Job Postings')
    ax.set_title('招聘岗位需求 Top10' if lang=='zh' else 'Top 10 Job Categories')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    fig.savefig(os.path.join(outdir, 'job_category_top10.png'), dpi=150, bbox_inches='tight'); plt.close(fig)

    # ---- Chart 6: Salary distribution ----
    fig, ax = plt.subplots(figsize=(12, 5))
    df['平均月薪'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
    ax.set_xlabel('平均月薪（元）' if lang=='zh' else 'Average Monthly Salary (CNY)')
    ax.set_ylabel('频次' if lang=='zh' else 'Frequency')
    ax.set_title('薪资分布直方图' if lang=='zh' else 'Salary Distribution')
    fig.savefig(os.path.join(outdir, 'salary_distribution.png'), dpi=150, bbox_inches='tight'); plt.close(fig)

    print(f"[{lang}] all charts -> images/{lang}/")


if __name__ == '__main__':
    make('zh')
    make('en')
    print("Done.")
