# -*- coding: utf-8 -*-
"""
generate_charts.py
Generate analysis charts from the cleaned recruitment data into images/.
Corresponds to Task 4: Data Visualization.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # headless backend, no GUI needed
import matplotlib.pyplot as plt

# Chinese fonts fallback for any CJK labels (kept for safety)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Path resolution (script lives in code/, project root is one level up)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'recruitment_data_cleaned.csv')
OUT_DIR = os.path.join(BASE_DIR, 'images')
os.makedirs(OUT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
print(f"Loaded: {len(df):,} records")

# Invalid job-category values (consistent with data_cleaning.py)
INVALID = ['全职', '-', '其他', '不限', 'nan', 'NaN', '', 'nan']


def save(fig, name):
    """Save a figure into the images/ directory."""
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {path}")


# ========== Chart 1: Top 10 industries by job count ==========
top_industry = df['上市公司行业'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
top_industry.sort_values().plot(kind='barh', ax=ax, color='steelblue')
ax.set_xlabel('Number of job posts')
ax.set_title('Top 10 Industries by Job Postings')
save(fig, 'industry_top10.png')

# ========== Chart 2: Top 10 cities by job count ==========
top_city = df['工作城市'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
top_city.sort_values().plot(kind='barh', ax=ax, color='coral')
ax.set_xlabel('Number of job posts')
ax.set_title('Top 10 Cities by Job Postings')
save(fig, 'city_top10.png')

# ========== Chart 3: Education requirement distribution ==========
edu_counts = df['学历_简化'].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
edu_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
ax.set_ylabel('')
ax.set_title('Education Requirement Distribution')
save(fig, 'education_distribution.png')

# ========== Chart 4: Top 10 industries by average salary ==========
# Keep only industries with enough samples for reliable means
valid_ind = df.groupby('上市公司行业').size()
industries = valid_ind[valid_ind >= 30].index
df_valid = df[df['上市公司行业'].isin(industries)]
salary_top = df_valid.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 6))
salary_top.sort_values().plot(kind='barh', ax=ax, color='green')
ax.set_xlabel('Average monthly salary (CNY)')
ax.set_title('Top 10 Industries by Average Salary')
save(fig, 'salary_top_industries.png')

# ========== Chart 5: Top 10 job categories ==========
job_col = '岗位分类'
df_job = df[~df[job_col].isin(INVALID) & df[job_col].notna() & (df[job_col] != '')]
job_top = df_job[job_col].value_counts().head(10)
fig, ax = plt.subplots(figsize=(12, 6))
job_top.plot(kind='bar', ax=ax, color='purple')
ax.set_xlabel('Job category')
ax.set_ylabel('Number of job posts')
ax.set_title('Top 10 Job Categories')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
save(fig, 'job_category_top10.png')

# ========== Chart 6: Salary distribution histogram ==========
fig, ax = plt.subplots(figsize=(12, 5))
df['平均月薪'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.set_xlabel('Average monthly salary (CNY)')
ax.set_ylabel('Frequency')
ax.set_title('Salary Distribution')
save(fig, 'salary_distribution.png')

print("All charts generated.")
