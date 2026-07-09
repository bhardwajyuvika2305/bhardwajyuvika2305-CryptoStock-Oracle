# 🌌 CryptoStock_Oracle: Data Science Research Report (Day 2 Milestone)

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Interactive Canvas](https://img.shields.io/badge/Engine-Plotly-orange.svg?style=for-the-badge&logo=plotly)](https://plotly.com)
[![UI Prototyping](https://img.shields.io/badge/UI-Streamlit_Ready-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

An interactive financial data science pipeline constructed to extract, analyze, and map time-series anomalies across traditional stock markets and cryptocurrency networks. 🏦 📈

This repository documents the active progress of the **45-Day Summer Industrial Training (4th Semester, 2026)**. 🎓

---

## 🏛️ Project Objective & Selection Thesis

Traditional equity auctions operate on fixed schedules (Monday–Friday), while digital currency asset protocols process blocks continuously ($24 \times 7 \times 365$). This introduces significant data gaps, weekend volatility adjustments, and unique trading regimes. ⏳

### 🎯 Core Focus Areas:
1. **📡 Financial Vectorization:** Learning to extract and transform live raw records using a focused Python data science stack rather than pre-cleaned static datasets.
2. **🎨 Interactive Graphic Design:** Moving away from static flat charts into responsive visual matrix pipelines using Plotly and custom UI layouts.
3. **✨ Glassmorphic Presentation Interface:** Preparing a premium interface by combining Streamlit with custom HTML5/CSS3 frosted-glass components.

---
### Core Focus Areas:
1. **🧠 Financial Vectorization:** Learning to extract and transform live raw records using a focused Python data science stack rather than pre-cleaned static datasets.
2. **📡 Interactive Graphic Design:** Moving away from static flat charts into responsive visual matrix pipelines using Plotly and custom UI layers.
3. **🔢 Glassmorphic Presentation Interface:** Preparing a premium interface by combining Streamlit with custom CSS/HTML frosted-glass components.

---
## 📅 Table 1: Complete 45-Day Academic Syllabus Breakdown (Week-Wise)
*This table represents the core curriculum taught during the industrial training course.* 📝

| 🗓️ Week | 🔢 Days | 📝 Core Training Course Syllabus Domain | 🛠️ Hands-On Skills Mastered |
| :--- | :--- | :--- | :--- |
| **Week 1** | Days 1–7 | Python Fundamentals & Environment Management | Setting up repositories, directory path structures, handling dependencies, and tracking versions. |
| **Week 2** | Days 8–14 | Financial Data Harvesting via APIs | Importing `yfinance`, automating timestamps via `datetime`, and handling connection protocols. |
| **Week 3** | Days 15–21 | In-Memory Arrays with NumPy & Pandas | Managing structural dataframes, masking index alignments, and converting price variables into log returns. |
| **Week 4** | Days 22–28 | Interactive Analytics with Plotly Core | Building layered charts, configuring dual-axis subplots, and formatting global layouts. |
| **Week 5** | Days 29–35 | Native Visualizations with Matplotlib | Rendering standard distribution frequency bins, tracking outliers, and generating static metric reports. |
| **Week 6** | Days 36–42 | Application Architecture via Streamlit | Designing interactive UI web layouts, linking sliders, and updating charts based on inputs. |
| **Week 7** | Days 43–45 | Cloud Synchronization & Project Submission | Deploying operational scripts to servers and presenting the project to the evaluation panel. |

---

## 🚀 Table 2: Technical Project Implementation Roadmap (Day-Wise Build)
*This grid tracks the execution of the project code up to the current milestone.* 🛠️

| 📅 Day | 🗂️ Target Asset | 🧠 Source Domain | 💻 Technical Action & Progress Log Summary | ⚙️ Status |
| :--- | :--- | :--- | :--- | :--- |
| **Day 1** | `01_data_ingestion.ipynb` | **Course Syllabus** | Set up configuration metrics, initiated repository structures, and built the automated retrieval module using `yfinance` and `datetime`. Captured logs to `crypto_processed.csv`. | ✅ **Completed** |
| **Day 2** | `02_core_visualizations.ipynb` | **Course Syllabus** | Implemented continuous multi-period logarithmic formulas. Created interactive subplots for asset prices, Bollinger tracking bands, and weekly volume charts. | 🔄 *Next Action* |

---

## 🔬 Core Progress Report: Day 1 & Day 2 Implementations

### 1. 🧮 Mathematical Foundations & Vector Processing (Day 1)
Simple arithmetic returns fail across multi-period horizons because they are non-additive. To guarantee vertical and horizontal temporal additivity across both traditional equity breaks and continuous digital pipelines, the raw price inputs are converted into logarithmic return vectors:

$$R_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$$

Annualized realized volatility is calculated as the rolling standard deviation ($\sigma$) of continuous log returns over a fixed 21-day window:

$$\sigma_{\text{annualized}} = \sqrt{\frac{252}{n-1}\sum_{i=1}^{n}\left(R_i - \bar{R}\right)^2}$$

### 2. 📊 Graphics Infrastructure & Risk Distributions (Day 2)
Using `02_core_visualizations.ipynb`, the engine reads the cached data matrix and sets up dynamic visual monitors:
* **📈 Visual 1 & 2 (Line & Area Mix):** Combines standard closing lines with translucent `fillcolor` bands to highlight asset breakouts relative to calculated upper and lower Bollinger variance limits.
* **📉 Visual 3 & 4 (Statistical Distributions):** Uses automated frequency bins via `plotly` to analyze distribution profiles, alongside structural bar charts tracking trading activity across different days of the week.

---

## 🛠️ Active Technology Stack Specification

The framework limits its environment configurations exclusively to these standard tools:
* **📓 `jupyter & jupyterlab`**: Intermediary interactive runtime notebooks.
* **🔌 `yfinance`**: Financial API tool used to extract real-time historical financial records.
* **⏰ `datetime & time`**: Time management libraries used to configure trading window horizons.
* **🔮 `plotly`**: Renders all interactive graphs, responsive subplots, and correlation boundaries.
* **🐼 `pandas & numpy`**: Handles data table structures, missing fields, and vectorized arrays.
* **📊 `matplotlib`**: Generates back-end diagnostic charts.
* **🎨 `HTML5 & CSS3 (Glassmorphism)`**: Prepared for dashboard injection to style frosted-glass visual containers.

---

## 🔮 Educational Value: Finance & Tech Knowledge Acquired

* **In Quantitative Finance:** Deeply understood variance clustering, logarithmic returns, and how trading calendar gaps impact historical calculations across asset classes.
* **In Self-Directed Engineering:** Learned how to independently source, read, and implement advanced programming methods (like predictive models) outside the standard classroom syllabus to enhance my project.
## ⚙️ How to Initialize and Run the Day 2 Snapshot

---
1. **📥 Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/CryptoStock_Oracle.git](https://github.com/YOUR_GITHUB_USERNAME/CryptoStock_Oracle.git)
   cd CryptoStock_Oracle

