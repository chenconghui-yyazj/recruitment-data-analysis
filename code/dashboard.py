import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(page_title="上市公司招聘数据分析系统", layout="wide")
st.title("📊 上市公司招聘大数据分析系统")
st.markdown("基于2014-2016年上市公司招聘数据的就业趋势研判")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_csv('招聘数据_清洗后.csv', encoding='utf-8')
    return df

with st.spinner("正在加载数据..."):
    df = load_data()

st.sidebar.success(f"已加载 {len(df):,} 条记录")

# 侧边栏筛选
st.sidebar.header("🔍 数据筛选")
industries = ['全部'] + sorted(df['上市公司行业'].dropna().unique().tolist())
selected_industry = st.sidebar.selectbox("选择行业", industries)

cities = ['全部'] + sorted(df['工作城市'].dropna().unique().tolist()[:20])
selected_city = st.sidebar.selectbox("选择城市", cities)

# 过滤数据
filtered_df = df.copy()
if selected_industry != '全部':
    filtered_df = filtered_df[filtered_df['上市公司行业'] == selected_industry]
if selected_city != '全部':
    filtered_df = filtered_df[filtered_df['工作城市'] == selected_city]

# 指标卡片
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 总招聘量", f"{len(filtered_df):,}")
col2.metric("💰 平均月薪", f"{filtered_df['平均月薪'].mean():.0f} 元")
col3.metric("🏢 覆盖行业", f"{filtered_df['上市公司行业'].nunique()}")
col4.metric("📍 覆盖城市", f"{filtered_df['工作城市'].nunique()}")

st.markdown("---")

# 图表1：行业招聘Top10
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏢 招聘量最多的10个行业")
    industry_counts = filtered_df['上市公司行业'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    industry_counts.plot(kind='barh', ax=ax, color='steelblue')
    ax.set_xlabel('招聘数量')
    st.pyplot(fig)

# 图表2：城市招聘Top10
with col2:
    st.subheader("📍 招聘量最多的10个城市")
    city_counts = filtered_df['工作城市'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    city_counts.plot(kind='barh', ax=ax, color='coral')
    ax.set_xlabel('招聘数量')
    st.pyplot(fig)

st.markdown("---")

# 图表3：学历分布
col1, col2 = st.columns(2)
with col1:
    st.subheader("📚 学历要求分布")
    if '学历_简化' in filtered_df.columns:
        edu_counts = filtered_df['学历_简化'].value_counts()
    else:
        edu_counts = filtered_df['学历要求'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    edu_counts.head(6).plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_ylabel('')
    st.pyplot(fig)

# 图表4：高薪行业Top10
with col2:
    st.subheader("💰 平均薪资最高的10个行业")
    salary_by_industry = filtered_df.groupby('上市公司行业')['平均月薪'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    salary_by_industry.plot(kind='barh', ax=ax, color='green')
    ax.set_xlabel('平均月薪（元）')
    st.pyplot(fig)

st.markdown("---")

# 图表5：岗位需求Top10
st.subheader("📋 招聘岗位需求 Top10")
if '初级分类' in filtered_df.columns:
    invalid = ['全职', '-', '其他', '不限']
    df_no_invalid = filtered_df[~filtered_df['初级分类'].isin(invalid)]
    category_counts = df_no_invalid['初级分类'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    category_counts.plot(kind='bar', ax=ax, color='purple')
    ax.set_xlabel('岗位类别')
    ax.set_ylabel('招聘数量')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig)

st.markdown("---")

# 图表6：薪资分布
st.subheader("📈 薪资分布直方图")
fig, ax = plt.subplots(figsize=(12, 5))
filtered_df['平均月薪'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.set_xlabel('平均月薪（元）')
ax.set_ylabel('频次')
ax.set_title('薪资分布')
st.pyplot(fig)

st.markdown("---")

# 数据预览
st.subheader("📄 数据样本预览")
display_cols = ['上市公司行业', '工作城市', '学历要求', '初级分类', '平均月薪']
available_cols = [c for c in display_cols if c in filtered_df.columns]
st.dataframe(filtered_df[available_cols].head(100))

st.markdown("---")
st.caption("数据来源：上市公司招聘大数据2014-2016 | 分析系统：Streamlit")