# 🏡 Nashville Housing Market Intelligence Dashboard

[![Deployed on GitHub Pages](https://img.shields.io/badge/Deployed_on-GitHub_Pages-blue?logo=github)](https://muhammadrao53.github.io/nashville-housing-dashboard/)
[![Made with HTML/JS](https://img.shields.io/badge/Frontend-HTML%20%7C%20JS-orange.svg)]()
[![Powered by Chart.js](https://img.shields.io/badge/Visuals-Chart.js-lightgrey.svg)](https://www.chartjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive, browser-based data analytics and business intelligence platform exploring property transactions, valuation dynamics, structural housing characteristics, and temporal trends across Davidson County, Nashville, Tennessee.

---

## 🚀 Live Demo
Experience the interactive application live on the web—no installation required:
👉 **[Access the Nashville Housing Live Dashboard](https://muhammadrao53.github.io/nashville-housing-dashboard/)**

---

## 📊 Executive Summary & Project Architecture
Real estate markets are complex ecosystems driven by macroeconomic shifts, municipal zoning laws, and structural attributes. This dashboard bridges raw Davidson County property deeds with interactive web analytics, empowering investors, urban planners, and analysts to explore market trends dynamically.

Transitioned to a lightweight, client-side web application, the dashboard provides seamless, instant interactivity directly in the browser, featuring:
* **📖 Market Overview & Trends:** High-level interactive visualizations mapping out the local real estate landscape.
* **🔍 Granular Insights:** Deep dives into price distributions, temporal transaction volume, and structural property premiums.

---

## 🛠️ Data Engineering & Cleaning Pipeline
Raw real estate records are notoriously messy. While this dashboard runs entirely in the browser, the data driving it was rigorously preprocessed offline using **Python (`pandas`)**:
* **Spatial Address Imputation:** Recovered missing street addresses by leveraging grouped parcel identifiers (`ParcelID`) via forward and backward filling algorithms to prevent data loss.
* **Deduplication Strategy:** Filtered out redundant entries using a composite primary key (`ParcelID`, `PropertyAddress`, `SalePrice`, `LegalReference`), distilling the database down to **56,373 high-integrity unique transactions**.
* **Type Standardization:** Parsed raw timestamps and cleaned financial strings to generate the clean aggregate datasets utilized by the frontend charting library.

---

## 📈 Visual Analytics & Color Coding Guide
Every chart in the overview is deliberately designed to communicate specific market phenomena:
* 🟦 **Sale Price Distribution (Histogram | Teal `#4ecdc4`):** Displays pricing density and right-skewness, illustrating how luxury properties pull the mean ($327,523) above the median ($205,700).
* 🟥 **Monthly Transaction Volume (Line Chart | Coral Red `#ff6b6b`):** Tracks market liquidity and seasonal buying behavior over time, highlighting transaction peaks and macroeconomic contractions.
* 🟩🟨 **Average Sale Price by Tax District (Horizontal Bar Chart):** Compares property valuations across municipal tax jurisdictions (e.g., Urban Services vs. exclusive suburban enclaves like Belle Meade and Forest Hills).
* 🟪 **Price Variance by Bedroom Count (Box Plot / Bar):** Dissects the structural "bedroom premium" and pricing dispersion across room tiers.

---

## 🧰 Tech Stack & Libraries
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Data Visualization:** Chart.js (via CDN)
* **Data Preprocessing (Offline):** Python, Pandas, NumPy
* **Version Control & Deployment:** Git, GitHub Pages

---

## ⚙️ Local Installation & Setup
Because this dashboard is built using standard web technologies, running it locally takes seconds. No servers, virtual environments, or package installations are required.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/muhammadrao53/nashville-housing-dashboard.git](https://github.com/muhammadrao53/nashville-housing-dashboard.git)
   cd nashville-housing-dashboard
