# -*- coding: utf-8 -*-
"""
dashboard.py
Interactive Streamlit dashboard for listed-company recruitment data analysis.
Run:  streamlit run code/dashboard.py
"""
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Chinese font fallback for CJK labels
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Page config
st.set_page_config(page_title="Listed-Company Recruitment Analysis System", layout="wide")
st.title("📊 Listed-Company Recruitment Big Data Analysis System")
st.markdown("Employment trend analysis based on listed-company recruitment data")


@st.cache_data
def load_data():
    """Load cleaned recruitment data."""
    df = pd.read_csv('data/recruitment_data_cleaned.csv', encoding='utf-8')
    return df


with st.spinner("Loading data..."):
    df = load_data()

st.sidebar.success(f"Loaded {len(df):,} records")

# Sidebar filters
st.sidebar.header("🔍 Data Filters")
industries = ['All'] + sorted(df['上市公司行业'].dropna().unique().tolist())
selected_industry = st.sidebar.selectbox("Select industry", industries)

cities = ['All'] + sorted(df['工作城市'].dropna().unique().tolist()[:20])
selected_city = st.sidebar.selectbox("Select city", cities)

# Filter data
filtered_df = df.copy()
if selected_industry != 'All':
    filtered_df = filtered_df[filtered_df['上市公司行业'] == selected_industry]
if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['工作城市'] == selected_city]

# KPI cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total Job Posts", f"{len(filtered_df):,}")
col2.metric("💰 Avg. Monthly Salary", f"{filtered_df['平均月薪'].mean():.0f} CNY")
col3.metric("🏢 Industries Covered", f"{filtered_df['上市公司行业'].nunique()}")
col4.metric("📍 Cities Covered", f"{filtered_df['工作城市'].nunique()}")

st.markdown("---")

# Chart 1: Top 10 industries
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏢 Top 10 Industries by Job Postings")
    industry_counts = filtered_df['上市公司行业'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    industry_counts.plot(kind='barh', ax=ax, color='steelblue')
    ax.set_xlabel('Number of job posts')
    st.pyplot(fig)

# Chart 2: Top 10 cities
with col2:
    st.subheader("📍 Top 10 Cities by Job Postings")
    city_counts = filtered_df['工作城市'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    city_counts.plot(kind='barh', ax=ax, color='coral')
    ax.set_xlabel('Number of job posts')
    st.pyplot(fig)

st.markdown("---")

# Chart 3: Education distribution
col1, col2 = st.columns(2)
with col1:
    st.subheader("📚 Education Requirement Distribution")
    if '学历_简化' in filtered_df.columns:
        edu_counts = filtered_df['学历_简化'].value_counts()
    else:
        edu_counts = filtered_df['学历要求'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    edu_counts.head(6).plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_ylabel('')
    st.pyplot(fig)

# Chart 4: Top salary industries
with col2:
    st.subheader("💰 Top 10 Industries by Average Salary")
    salary_by_industry = filtered_df.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    salary_by_industry.plot(kind='barh', ax=ax, color='green')
    ax.set_xlabel('Average monthly salary (CNY)')
    st.pyplot(fig)

st.markdown("---")

# Chart 5: Top 10 job categories
st.subheader("📋 Top 10 Job Categories")
if '初级分类' in filtered_df.columns:
    invalid = ['全职', '-', '其他', '不限']
    df_no_invalid = filtered_df[~filtered_df['初级分类'].isin(invalid)]
    category_counts = df_no_invalid['初级分类'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    category_counts.plot(kind='bar', ax=ax, color='purple')
    ax.set_xlabel('Job category')
    ax.set_ylabel('Number of job posts')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig)

st.markdown("---")

# Chart 6: Salary distribution
st.subheader("📈 Salary Distribution Histogram")
fig, ax = plt.subplots(figsize=(12, 5))
filtered_df['平均月薪'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.set_xlabel('Average monthly salary (CNY)')
ax.set_ylabel('Frequency')
ax.set_title('Salary Distribution')
st.pyplot(fig)

st.markdown("---")

# Data preview
st.subheader("📄 Data Sample Preview")
display_cols = ['上市公司行业', '工作城市', '学历要求', '初级分类', '平均月薪']
available_cols = [c for c in display_cols if c in filtered_df.columns]
st.dataframe(filtered_df[available_cols].head(100))

st.markdown("---")
st.caption("Source: Listed-company recruitment data | Built with Streamlit")
