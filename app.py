import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Nashville Housing Market", page_icon="🏡", layout="wide")

st.title("🏡 Nashville Housing Market Analysis & Explorer")
st.markdown("An interactive portfolio dashboard analyzing property transactions, pricing distributions, and valuation trends.")

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
tab1, tab2 = st.tabs(["📊 Market Overview & Trends", "🔍 Interactive Property Explorer"])

with tab1:
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

with tab2:
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
