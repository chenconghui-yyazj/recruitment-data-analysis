# Listed-Company Recruitment Big Data: Talent Demand Analysis & Employment Trend Study

> An end-to-end data analysis project on listed-company recruitment data (2014–2026): data governance → multi-dimensional analysis → trend forecasting → visualization → practical applications, revealing the structure and evolution of talent demand across industries, cities, education levels, and job categories.

> **🌐 Bilingual** · This is the **English** version (primary). 中文版见 [`README_中文.md`](README_中文.md) / Chinese version available in [`README_中文.md`](README_中文.md).

## 📌 About the Project

This project conducts a complete data-analysis and applied-research workflow on **listed-company recruitment big data**, covering **Data Governance → Feature Analysis → Trend Forecasting → Visualization → Application Value**. The data includes multi-dimensional information such as job category, education requirement, salary level, work location, industry distribution, and publish time.

The cleaned dataset contains **323,818** valid job records with **10** standardized fields.

## 🎯 Objectives (corresponding to the three competition tasks)

| Task | Content |
| --- | --- |
| ① Data Cleaning & Governance | Cleaning, deduplication, missing-value handling, outlier detection, field standardization |
| ② Demand Feature Analysis | Industry differences, regional distribution, education structure, job categories, time trends |
| ③ Hot Jobs & Demand Changes | Identify fastest-growing jobs, active industries/regions, education & skill changes over time |

## 🛠 Tech Stack

- **Python 3** + pandas / numpy / scipy / matplotlib / seaborn
- **Streamlit** interactive visualization dashboard
- **Matplotlib / Seaborn** static analysis charts

## 📁 Repository Structure

```
recruitment-data-analysis/
├── README.md                    # Project overview — English (this file)
├── README_中文.md               # Project overview — Chinese version
├── 数据分析报告.md              # Analysis report — English (primary)
├── 数据分析报告_中文.md         # Analysis report — Chinese version
├── 数据清洗说明文档.md          # Data cleaning documentation — English
├── 数据清洗说明文档_中文.md     # Data cleaning documentation — Chinese
├── requirements.txt             # Dependencies
├── data/
│   └── recruitment_data_cleaned.csv   # Cleaned dataset (323,818 records)
├── code/
│   ├── data_cleaning.py         # Data cleaning & analysis main script
│   ├── dashboard.py             # Streamlit interactive dashboard
│   └── generate_charts.py       # Chart generation script
├── images/                      # Analysis charts (English titles)
└── docs/
    └── task_description.pdf     # Official competition task description
```

## 💡 Highlights / Key Findings

- **Rigorous data governance**: IQR-based salary outlier removal, missing-value & duplicate handling, field standardization — fully reproducible.
- **Multi-dimensional insights**: panoramic view of industry / city / education / job demand structure.
- **Trend forecasting**: identifies hot jobs and talent-demand shifts over time.
- **Interactive visualization**: Streamlit dashboard with real-time filtering by industry & city.

## ▶️ How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run data analysis (generates cleaning report & charts)
python code/data_cleaning.py

# 3. Launch interactive dashboard
streamlit run code/dashboard.py
```

> Note: `data_cleaning.py` requires the full raw recruitment dataset to run; `data/recruitment_data_cleaned.csv` is the cleaned result ready for analysis.

## 📈 Preview

Analysis charts are available in the `images/` directory (industry, city, education, salary, job category, etc.).

## ✍️ Author

**Chen Conghui (陈聪惠)** · Guangzhou Business School · Big Data Management & Application
Data Analysis / Data Visualization · Portfolio Project #1

---

*Project completed independently based on a competition task. Code and data processing are fully open-sourced.*
