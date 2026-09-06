# 🏡 Nashville Housing Market Intelligence Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nashville-housing-dashboard-9wn8etvjyeut3fn5o83ab.streamlit.app)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end data analytics and business intelligence platform exploring property transactions, valuation dynamics, structural housing characteristics, and temporal trends across Davidson County, Nashville, Tennessee.

---

## 🚀 Live Demo
Experience the interactive application live in the cloud:
👉 **[Access Nashville Housing Live Dashboard](https://nashville-housing-dashboard-9wn8etvyyeut3yfn5o83ab.streamlit.app/)**

---

## 📊 Executive Summary & Project Architecture
Real estate markets are complex ecosystems driven by macroeconomic shifts, municipal zoning laws, and structural attributes. This dashboard bridges raw Davidson County property deeds with interactive analytics, empowering investors, urban planners, and analysts to explore market trends dynamically.

The application is structured into a multi-tab analytical workflow:
1. **📖 Comprehensive Executive Report:** Deep-dive documentation explaining dataset provenance, data engineering pipeline choices, statistical distributions, and chart color-coding logic.
2. **📊 Market Overview & Trends:** High-level interactive visualizations with multi-variable sidebar filtering (Price ranges, sale years, land use categories, and bedroom counts).
3. **🔍 Interactive Property Explorer:** Granular text search across property street addresses with live data filtering and a **CSV export option** for offline financial modeling.

---

## 🛠️ Data Engineering & Cleaning Pipeline
Raw real estate records are notoriously messy. The following preprocessing steps were executed using **Python (`pandas`)** prior to visualization:
* **Spatial Address Imputation:** Recovered missing street addresses by leveraging grouped parcel identifiers (`ParcelID`) via forward and backward filling algorithms (`bfill`/`ffill`) to prevent data loss.
* **Deduplication Strategy:** Filtered out redundant entries using a composite primary key (`ParcelID`, `PropertyAddress`, `SalePrice`, `LegalReference`), distilling the database down to **56,373 high-integrity unique transactions**.
* **Type Standardization:** Parsed raw timestamps into datetime objects for precise monthly/yearly aggregation and cleaned financial strings into float types for mathematical modeling.

---

## 📈 Visual Analytics & Color Coding Guide
Every chart in the overview tab is deliberately designed to communicate specific market phenomena:
* 🟦 **Sale Price Distribution (Histogram | Teal `#4ecdc4`):** Displays pricing density and right-skewness, illustrating how luxury properties pull the mean ($\$327,523$) above the median ($\$205,700$).
* 🟥 **Monthly Transaction Volume (Line Chart | Coral Red `#ff6b6b`):** Tracks market liquidity and seasonal buying behavior over time, highlighting transaction peaks and macroeconomic contractions.
* 🟩🟨 **Average Sale Price by Tax District (Horizontal Bar Chart):** Compares property valuations across municipal tax jurisdictions (e.g., Urban Services vs. exclusive suburban enclaves like Belle Meade and Forest Hills).
* 🟪 **Price Variance by Bedroom Count (Box Plot):** Dissects the structural "bedroom premium" and pricing dispersion across room tiers.

---

## 🧰 Tech Stack & Libraries
* **Core Language:** Python
* **Data Manipulation & Cleaning:** Pandas, NumPy
* **Data Visualization:** Plotly Express, Matplotlib
* **Dashboard Framework:** Streamlit
* **Version Control & Deployment:** Git, GitHub, Streamlit Community Cloud

---

## ⚙️ Local Installation & Setup
To run this application locally on your machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/muhammadrao53/nashville-housing-dashboard.git](https://github.com/muhammadrao53/nashville-housing-dashboard.git)
   cd nashville-housing-dashboard
