# -*- coding: utf-8 -*-
"""
data_cleaning.py
Clean and analyze the listed-company recruitment big data.
Pipeline: read raw data -> standardize fields -> convert salary -> clean -> analyze -> save.

Note: Full run requires the raw recruitment dataset
(上市公司招聘大数据2014-2026.3.csv) which is large; the cleaned result
is already provided in data/recruitment_data_cleaned.csv.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# ========== 1. Read data and probe fields ==========
print("Reading data in chunks...")
chunk_size = 100000
sample_frac = 0.05  # 5% sampling
chunks = []
total_rows = 0

# Read first chunk to inspect column names
first_chunk = pd.read_csv('上市公司招聘大数据2014-2026.3.csv',
                          encoding='utf-8',
                          nrows=5)
print("\n=== Data fields ===")
for i, col in enumerate(first_chunk.columns):
    print(f"{i + 1}. {col}")

for chunk in pd.read_csv('上市公司招聘大数据2014-2026.3.csv',
                         encoding='utf-8',
                         low_memory=False,
                         chunksize=chunk_size):
    sampled = chunk.sample(frac=sample_frac, random_state=42)
    chunks.append(sampled)
    total_rows += len(chunk)
    print(f"Processed {total_rows:,} rows...", end='\r')

df = pd.concat(chunks, ignore_index=True)
print(f"\nRaw data ~{total_rows:,} rows, sampled {len(df):,} rows")

# ========== 2. Field standardization ==========
print("\n=== Field mapping & standardization ===")

# Keep a copy of original column names
original_columns = df.columns.tolist()

# Create new field mapping (avoid duplicates)
field_mapping = {}

# Time field
if '招聘发布日期' in df.columns:
    field_mapping['招聘发布日期'] = '发布时间'
    print(f"Time field: 招聘发布日期 -> 发布时间")
elif '招聘结束日期' in df.columns:
    field_mapping['招聘结束日期'] = '发布时间'
    print(f"Time field: 招聘结束日期 -> 发布时间")

# Industry field
if '上市公司行业' in df.columns:
    print(f"Industry field: 上市公司行业")

# City field
if '工作城市' in df.columns:
    print(f"City field: 工作城市")

# Education field
if '学历要求' in df.columns:
    print(f"Education field: 学历要求")

# Job field - prefer primary category, fallback to job title
if '初级分类' in df.columns and '初级分类' not in field_mapping.values():
    field_mapping['初级分类'] = '岗位分类'
    print(f"Job field: 初级分类 -> 岗位分类")
elif '招聘岗位' in df.columns:
    field_mapping['招聘岗位'] = '岗位分类'
    print(f"Job field: 招聘岗位 -> 岗位分类")

# Salary field
if '最低月薪' in df.columns and '最高月薪' in df.columns:
    print(f"Salary field: 最低月薪、最高月薪")

# Apply field renaming
df = df.rename(columns=field_mapping)

print(f"\nStandardized fields: {df.columns.tolist()}")


# ========== 3. Salary conversion ==========
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

# ========== 4. Data cleaning ==========
print("\n=== Data cleaning ===")
initial_count = len(df)

# Drop records with invalid salary
df_clean = df.dropna(subset=['最低月薪_数值', '最高月薪_数值'])
df_clean = df_clean[(df_clean['最低月薪_数值'] > 0) & (df_clean['最高月薪_数值'] > 0)]
df_clean = df_clean[df_clean['最高月薪_数值'] >= df_clean['最低月薪_数值']]

# IQR method to identify salary outliers
Q1 = df_clean['最高月薪_数值'].quantile(0.25)
Q3 = df_clean['最高月薪_数值'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
salary_outliers = df_clean[(df_clean['最高月薪_数值'] < lower_bound) |
                           (df_clean['最高月薪_数值'] > upper_bound)]
print(f"Salary outliers identified: {len(salary_outliers)} records ({len(salary_outliers) / len(df_clean) * 100:.2f}%)")

# Remove salary outliers
df_clean = df_clean[(df_clean['最高月薪_数值'] >= lower_bound) &
                    (df_clean['最高月薪_数值'] <= upper_bound)]

# Drop rows with missing key fields
required_cols = ['学历要求', '上市公司行业', '工作城市']
existing_required = [col for col in required_cols if col in df_clean.columns]
df_clean = df_clean.dropna(subset=existing_required)
df_clean['平均月薪'] = (df_clean['最低月薪_数值'] + df_clean['最高月薪_数值']) / 2

# Remove duplicates
df_clean = df_clean.drop_duplicates()

print(f"Sampled data: {len(df):,} rows")
print(f"Cleaned data: {len(df_clean):,} rows")
print(f"Retention rate: {len(df_clean) / len(df) * 100:.2f}%")

# ========== 5. Time processing ==========
print("\n=== Time processing ===")

# Check if publish-time field exists
if '发布时间' in df_clean.columns:
    df_clean['发布时间'] = pd.to_datetime(df_clean['发布时间'], errors='coerce')
    df_clean = df_clean.dropna(subset=['发布时间'])
    df_clean['年份'] = df_clean['发布时间'].dt.year
    df_clean['月份'] = df_clean['发布时间'].dt.month
    df_clean['年月'] = df_clean['发布时间'].dt.to_period('M')

    # Filter valid years
    df_clean = df_clean[(df_clean['年份'] >= 2014) & (df_clean['年份'] <= 2026)]
    print(f"Valid year range: {df_clean['年份'].min()} - {df_clean['年份'].max()}")
else:
    # Fallback: use recruitment publish year
    if '招聘发布年份' in df_clean.columns:
        df_clean['年份'] = df_clean['招聘发布年份']
        df_clean['月份'] = 1  # default month
        print(f"Using publish-year field, range: {df_clean['年份'].min()} - {df_clean['年份'].max()}")
    else:
        print("Warning: no time field found, creating simulated time")
        df_clean['年份'] = 2015
        df_clean['月份'] = 1


# ========== 6. Simplify education ==========
def simplify_edu(edu):
    if pd.isna(edu):
        return 'Unknown'
    edu_str = str(edu)
    if '博士' in edu_str:
        return 'PhD'
    elif '硕士' in edu_str:
        return 'Master'
    elif '本科' in edu_str:
        return 'Bachelor'
    elif '大专' in edu_str:
        return 'Associate'
    elif '不限' in edu_str or '无' in edu_str or '不限制' in edu_str:
        return 'Open'
    else:
        return 'Other'


df_clean['学历_简化'] = df_clean['学历要求'].apply(simplify_edu)

# ========== 7. Statistical analysis ==========
print("\n=== Top 10 industries by job postings ===")
industry_counts = df_clean['上市公司行业'].value_counts().head(10)
print(industry_counts)

print("\n=== Top 10 cities by job postings ===")
city_counts = df_clean['工作城市'].value_counts().head(10)
print(city_counts)

print("\n=== Education distribution ===")
edu_simple = df_clean['学历_简化'].value_counts()
print(edu_simple)

# Fix job-category field issue
print("\n=== Top 10 job categories ===")
# Use the correct job field name
job_field = None
if '岗位分类' in df_clean.columns:
    job_field = '岗位分类'
elif '初级分类' in df_clean.columns:
    job_field = '初级分类'
elif '招聘岗位' in df_clean.columns:
    job_field = '招聘岗位'

if job_field:
    # Filter invalid categories
    invalid_cats = ['全职', '-', '其他', '不限', 'nan', 'NaN']
    df_valid_job = df_clean[~df_clean[job_field].isin(invalid_cats)]
    category_counts = df_valid_job[job_field].value_counts().head(10)
    print(category_counts)
else:
    print("Job field not found")
    category_counts = pd.Series()

# Top 10 industries by average salary (filter small samples)
print("\n=== Top 10 industries by average salary ===")
industry_counts_valid = df_clean.groupby('上市公司行业').size()
valid_industries = industry_counts_valid[industry_counts_valid >= 30].index
df_valid = df_clean[df_clean['上市公司行业'].isin(valid_industries)]
industry_salary_valid = df_valid.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
print(industry_salary_valid)

# ========== 8. Hot job identification ==========
print("\n=== Hot jobs (fastest-growing categories) ===")
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
            growth_df = pd.DataFrame(list(growth_rates.items()), columns=['Job', 'Growth%'])
            growth_df = growth_df.sort_values('Growth%', ascending=False).head(10)
            print(f"\nTop 10 fastest-growing jobs ({start_year} -> {end_year}):")
            print(growth_df)
        else:
            print("Cannot compute job growth rates")
    else:
        print("Not enough year data to compute growth")
else:
    print("Job field or year data insufficient")

# ========== 9. Time trend analysis ==========
print("\n=== Time trend analysis ===")
if '年月' in df_clean.columns and len(df_clean['年月'].unique()) > 1:
    monthly_trend = df_clean.groupby('年月').size()
    print(f"Average monthly postings: {monthly_trend.mean():.0f}")
    print(f"Peak months (Top3):")
    print(monthly_trend.sort_values(ascending=False).head(3))

    # Salary trend
    if len(df_clean['年份'].unique()) >= 2:
        salary_trend = df_clean.groupby('年份')['平均月薪'].mean()
        if len(salary_trend) >= 2:
            growth_rate = (salary_trend.iloc[-1] / salary_trend.iloc[0] - 1) * 100
            print(f"\nSalary annual growth rate: {growth_rate:.1f}%")
            print("\nAverage salary by year:")
            print(salary_trend)
else:
    print("Time data insufficient, skipping trend analysis")

# ========== 10. Save cleaned data ==========
# Select key fields to save
save_columns = ['上市公司行业', '工作城市', '学历要求', '学历_简化', '岗位分类',
                '平均月薪', '最低月薪_数值', '最高月薪_数值', '年份', '月份']
existing_save_cols = [col for col in save_columns if col in df_clean.columns]
if '岗位分类' not in existing_save_cols and job_field:
    existing_save_cols.append(job_field)

df_save = df_clean[existing_save_cols]
df_save.to_csv('recruitment_data_cleaned.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Cleaned data saved: recruitment_data_cleaned.csv ({len(df_save)} rows, {len(existing_save_cols)} fields)")

# ========== 11. Generate cleaning report ==========
print("\n" + "=" * 60)
print("Data Cleaning Report")
print("=" * 60)
print(f"Raw total rows: {total_rows:,}")
print(f"Sampling ratio: {sample_frac * 100}%")
print(f"Sampled rows: {len(df):,}")
print(f"Cleaned rows: {len(df_clean):,}")
print(f"Retention rate: {len(df_clean) / len(df) * 100:.2f}%")
print(f"Valid years: {df_clean['年份'].min()} - {df_clean['年份'].max()}")
print(f"Industries covered: {df_clean['上市公司行业'].nunique()}")
print(f"Cities covered: {df_clean['工作城市'].nunique()}")
if job_field:
    print(f"Job categories covered: {df_clean[job_field].nunique()}")
print("=" * 60)

# Save report to file
with open('data_cleaning_report.txt', 'w', encoding='utf-8') as f:
    f.write("Listed-Company Recruitment Data Cleaning Report\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Raw total rows: {total_rows:,}\n")
    f.write(f"Sampling ratio: {sample_frac * 100}%\n")
    f.write(f"Sampled rows: {len(df):,}\n")
    f.write(f"Cleaned rows: {len(df_clean):,}\n")
    f.write(f"Retention rate: {len(df_clean) / len(df) * 100:.2f}%\n\n")
    f.write("Main cleaning steps:\n")
    f.write("1. Salary outliers removed (IQR method)\n")
    f.write("2. Missing values dropped (industry, city, education)\n")
    f.write("3. Duplicate records removed\n")
    f.write("4. Time field parsed and filtered\n\n")
    f.write(f"Final dataset: {len(df_clean):,} valid job records\n")
    f.write(f"Time range: {df_clean['年份'].min()} - {df_clean['年份'].max()}\n")
    f.write(f"Industries covered: {df_clean['上市公司行业'].nunique()}\n")
    f.write(f"Cities covered: {df_clean['工作城市'].nunique()}\n")

print("\n✅ Analysis complete!")
