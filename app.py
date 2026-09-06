import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Nashville Housing Market", page_icon="🏡", layout="wide")

st.title("🏡 Nashville Housing Market Analysis & Comprehensive Report")
st.markdown("An exhaustive data science portfolio project examining real estate valuation, transaction velocity, structural housing characteristics, and spatial pricing dynamics in Nashville, Tennessee.")

# Load Data securely
@st.cache_data
def load_data():
    df = pd.read_csv("Nashville_Housing_Cleaned.csv")
    df['SaleDate'] = pd.to_datetime(df['SaleDate'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

# --- Navigation Tabs ---
tab1, tab2, tab3 = st.tabs(["📖 Comprehensive Executive Report", "📊 Market Overview & Trends", "🔍 Interactive Property Explorer"])

with tab1:
    st.header("Executive Summary & Analytical Context")
    st.markdown("""
    Real estate markets are complex ecosystems driven by macroeconomic shifts, zoning regulations, neighborhood infrastructure, and structural property characteristics. This report provides an in-depth empirical examination of the Nashville, Tennessee housing market utilizing transactional records from Davidson County. 

    By synthesizing data cleaning, statistical modeling, and interactive visualization, this dashboard bridges raw property deeds with actionable market intelligence for investors, urban planners, and real estate analysts.
    """)

    st.subheader("1. Dataset Provenance & Data Engineering Pipeline")
    st.markdown(f"""
    The analysis is built upon an exhaustive dataset comprising **{len(df):,} cleaned property transactions** spanning from **{df['SaleDate'].min().strftime('%B %Y')} to {df['SaleDate'].max().strftime('%B %Y')}**. Raw municipal property deeds are notoriously unstructured and susceptible to anomalies. To achieve analytical rigor, a rigorous data engineering pipeline was implemented in Python (`pandas`):
    * **Spatial Address Imputation:** Raw datasets often contain missing property street addresses while retaining valid parcel identifiers. Using grouped parcel keys (`ParcelID`), forward and backward filling algorithms (`bfill()` and `ffill()`) were deployed to recover missing location data without introducing synthetic bias.
    * **Deduplication Strategy:** Real estate databases frequently log duplicate entries due to multi-parcel sales, title transfers, or recording errors. Redundant records were filtered out using a composite primary key (`ParcelID`, `PropertyAddress`, `SalePrice`, and `LegalReference`), distilling the database down to **{len(df):,} unique, high-integrity transactions**.
    * **Type Casting & Normalization:** Dates were parsed into standardized datetime objects to enable granular temporal grouping (monthly and yearly aggregates). Currency fields were cleaned of symbols and commas, casting them into high-precision floating-point numbers to facilitate accurate arithmetic aggregation.
    """)

    st.subheader("2. Statistical Breakdown & Market Characteristics")
    st.markdown(f"""
    A preliminary statistical assessment of the Nashville housing market reveals significant right-skewness in property valuations:
    * **Central Tendency & Dispersion:** The dataset exhibits a mean sale price of **${df['SalePrice'].mean():,.2f}** against a median sale price of **${df['SalePrice'].median():,.2f}**. This substantial positive divergence reflects high-end luxury and commercial transactions pulling the mean upward, while median pricing provides a truer representation of typical residential affordability.
    * **Zoning & Land Use Composition:** Residential structures dominate the market architecture. Single-family homes represent the largest volume (**{df[df['LandUse'] == 'SINGLE FAMILY'].shape[0]:,} transactions**), followed by residential condos (**{df[df['LandUse'] == 'RESIDENTIAL CONDO'].shape[0]:,} transactions**), vacant land parcels, and duplexes.
    * **Tax District Administration:** Transactions are distributed across distinct municipal tax jurisdictions, with the Urban Services District and General Services District handling the vast majority of volume, alongside suburban municipal enclaves such as Forest Hills, Oak Hill, and Belle Meade.
    """)

    st.subheader("3. Comprehensive Guide to Dashboard Visualizations & Color Coding")
    st.markdown("""
    Every visual element in the **Market Overview** tab is deliberately designed to communicate specific economic phenomena. Below is a detailed breakdown of each chart, its analytical purpose, and its color-coding rationale:
    """)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("""
        #### 🟦 1. Sale Price Distribution (Histogram)
        * **Analytical Purpose:** Illustrates the probability density and frequency distribution of home sale prices within the active filter parameters. It answers whether the market is dominated by starter homes or luxury estates.
        * **Color Choice:** Rendered in **Teal (`#4ecdc4`)**. Teal provides high visual contrast against dark themes without inducing cognitive fatigue, signaling stability and data density.
        * **Interpretation:** A heavily right-skewed distribution indicates affordable housing clustering near the lower bound with a long tail of multi-million dollar luxury listings.
        
        #### 🟩🟨 2. Average Sale Price by Tax District (Horizontal Bar Chart)
        * **Analytical Purpose:** Compares mean property valuation across Nashville's administrative tax jurisdictions, highlighting geographic wealth concentration and municipal valuation disparities.
        * **Color Choice:** Utilizes a **Categorical Palette** where each tax district is assigned a distinct hue.
        * **Interpretation:** Districts with higher municipal service levels or exclusive zoning rules (e.g., Belle Meade or Forest Hills) consistently display elevated price ceilings compared to outer general service districts.
        """)
    with col_r2:
        st.markdown("""
        #### 🟥 3. Monthly Transaction Volume Over Time (Line Chart)
        * **Analytical Purpose:** Tracks macro-economic activity and seasonal liquidity across time. Real estate is inherently cyclical; this chart exposes volume peaks (spring/summer buying seasons) and troughs (winter slowdowns or macroeconomic shocks).
        * **Color Choice:** Rendered in **Coral Red (`#ff6b6b`)** with prominent vertex markers. Red instantly draws the reviewer's eye to temporal volatility and transaction volume spikes.
        * **Interpretation:** Sharp downward troughs typically align with broader economic contractions or seasonal freezing of housing inventory.
        
        #### 🟪 4. Price Variance by Bedroom Count (Box Plot)
        * **Analytical Purpose:** Dissects the structural "bedroom premium." It demonstrates how median pricing and interquartile ranges expand as home size increases.
        * **Color Choice:** Multi-colored categorical boxes per bedroom tier.
        * **Interpretation:** Outliers in lower bedroom tiers (e.g., 1-bedroom luxury condos downtown) often challenge conventional square-footage pricing models, providing nuance to investors.
        """)

    st.subheader("4. Strategic Implications for Investors & Analysts")
    st.markdown("""
    By utilizing the interactive filters on the **Market Overview** tab and the property search capabilities on the **Property Explorer** tab, stakeholders can:
    1. **Identify Undervalued Corridors:** Filter by specific tax districts and year built brackets to spot historical pricing arbitrage.
    2. **Monitor Market Liquidity:** Assess how transaction volumes react across specific calendar years and price brackets.
    3. **Export Tailored Subsets:** Download customized CSV datasets directly for offline financial modeling and predictive valuation modeling.
    """)

with tab2:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Scenarios")

    price_range = st.sidebar.slider("Sale Price Range ($)", 0, 2000000, (50000, 1000000), step=25000)
    min_year, max_year = int(df['SaleDate'].dt.year.min()), int(df['SaleDate'].dt.year.max())
    year_range = st.sidebar.slider("Sale Year", min_year, max_year, (min_year, max_year))

    top_uses = df['LandUse'].value_counts().nlargest(10).index.tolist()
    selected_uses = st.sidebar.multiselect("Select Land Use Type", options=top_uses, default=["SINGLE FAMILY"])

    bed_filter = st.sidebar.slider("Maximum Bedrooms", 0, 10, 6)

    # Apply Filters
    mask = (
        (df['SalePrice'] >= price_range[0]) & 
        (df['SalePrice'] <= price_range[1]) &
        (df['SaleDate'].dt.year >= year_range[0]) &
        (df['SaleDate'].dt.year <= year_range[1]) &
        (df['LandUse'].isin(selected_uses)) &
        (df['Bedrooms'] <= bed_filter)
    )
    filtered_df = df[mask]

    # --- KPI Metrics Row ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Filtered Transactions", f"{len(filtered_df):,}")
    col2.metric("Average Sale Price", f"${filtered_df['SalePrice'].mean():,.0f}" if len(filtered_df) > 0 else "$0")
    col3.metric("Average Acreage", f"{filtered_df['Acreage'].mean():,.2f} acres" if len(filtered_df) > 0 else "0 acres")
    col4.metric("Avg Year Built", f"{int(filtered_df['YearBuilt'].mean())}" if len(filtered_df) > 0 and not pd.isna(filtered_df['YearBuilt'].mean()) else "N/A")

    st.markdown("---")

    # --- Interactive Visualizations ---
    r1_c1, r1_c2 = st.columns(2)

    with r1_c1:
        if len(filtered_df) > 0:
            fig_price = px.histogram(filtered_df, x="SalePrice", nbins=40, title="Sale Price Distribution", color_discrete_sequence=['#4ecdc4'])
            st.plotly_chart(fig_price, use_container_width=True)
        else:
            st.warning("No data available for this price filter.")

    with r1_c2:
        if len(filtered_df) > 0:
            sales_time = filtered_df.groupby(filtered_df['SaleDate'].dt.to_period('M')).size().reset_index(name='Counts')
            sales_time['SaleDate'] = sales_time['SaleDate'].dt.to_timestamp()
            fig_time = px.line(sales_time, x='SaleDate', y='Counts', title="Monthly Transaction Volume Over Time", markers=True, color_discrete_sequence=['#ff6b6b'])
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.warning("No data available for this date filter.")

    r2_c1, r2_c2 = st.columns(2)

    with r2_c1:
        if len(filtered_df) > 0:
            top_districts = filtered_df.groupby('TaxDistrict')['SalePrice'].mean().reset_index()
            fig_tax = px.bar(top_districts, x='SalePrice', y='TaxDistrict', orientation='h', title="Avg Sale Price by Tax District", color='TaxDistrict')
            st.plotly_chart(fig_tax, use_container_width=True)
        else:
            st.warning("No data available.")

    with r2_c2:
        if len(filtered_df) > 0:
            fig_box = px.box(filtered_df, x='Bedrooms', y='SalePrice', title="Price Variance by Bedroom Count", color='Bedrooms')
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("No data available.")

with tab3:
    st.header("Search & Filter Individual Properties")
    st.markdown("Use this raw explorer to examine records matching custom search terms.")
    
    search_query = st.text_input("Search Property Address", "")
    
    display_df = df.copy()
    if search_query:
        display_df = display_df[display_df['PropertyAddress'].str.contains(search_query, case=False, na=False)]
        
    st.dataframe(display_df[['PropertyAddress', 'SalePrice', 'SaleDate', 'LandUse', 'Bedrooms', 'FullBath', 'YearBuilt']].head(100), use_container_width=True)
    
    # Download button for filtered dataset
    csv_data = display_df.head(1000).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv_data,
        file_name='nashville_housing_filtered.csv',
        mime='text/csv',
    )
