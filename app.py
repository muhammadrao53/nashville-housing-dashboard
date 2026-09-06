import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Nashville Housing Market", layout="wide")
st.title("🏡 Nashville Housing Market Analysis")

# Load Data (cached for performance)
@st.cache_data
def load_data():
    df = pd.read_csv("Nashville_Housing_Cleaned.csv")
    df['SaleDate'] = pd.to_datetime(df['SaleDate'])
    return df

df = load_data()

# --- Sidebar Filters (The "Scenarios" functionality) ---
st.sidebar.header("Interactive Filters")

# Price Range Slider
price_range = st.sidebar.slider("Sale Price Range", 0, 2000000, (50000, 1000000), step=50000)

# Year Range Slider
min_year, max_year = df['SaleDate'].dt.year.min(), df['SaleDate'].dt.year.max()
year_range = st.sidebar.slider("Sale Year", int(min_year), int(max_year), (int(min_year), int(max_year)))

# Property Type Multiselect
top_uses = df['LandUse'].value_counts().nlargest(10).index.tolist()
selected_uses = st.sidebar.multiselect("Select Land Use", options=top_uses, default=["SINGLE FAMILY"])

# --- Filter Application ---
mask = (
    (df['SalePrice'] >= price_range[0]) & 
    (df['SalePrice'] <= price_range[1]) &
    (df['SaleDate'].dt.year >= year_range[0]) &
    (df['SaleDate'].dt.year <= year_range[1]) &
    (df['LandUse'].isin(selected_uses))
)
filtered_df = df[mask]

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{len(filtered_df):,}")
col2.metric("Average Sale Price", f"${filtered_df['SalePrice'].mean():,.0f}")
col3.metric("Average Acreage", f"{filtered_df['Acreage'].mean():,.2f} acres")
col4.metric("Avg Year Built", f"{int(filtered_df['YearBuilt'].mean()) if not pd.isna(filtered_df['YearBuilt'].mean()) else 0}")

st.markdown("---")

# --- Visualizations ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    fig_price = px.histogram(filtered_df, x="SalePrice", nbins=50, title="Sale Price Distribution", color_discrete_sequence=['#0083B8'])
    st.plotly_chart(fig_price, use_container_width=True)

with row1_col2:
    sales_time = filtered_df.groupby(filtered_df['SaleDate'].dt.to_period('M')).size().reset_index(name='Counts')
    sales_time['SaleDate'] = sales_time['SaleDate'].dt.to_timestamp()
    fig_time = px.line(sales_time, x='SaleDate', y='Counts', title="Transaction Volume Over Time", markers=True, color_discrete_sequence=['#FF4B4B'])
    st.plotly_chart(fig_time, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    district_price = filtered_df.groupby('TaxDistrict')['SalePrice'].mean().reset_index()
    fig_tax = px.bar(district_price, x='SalePrice', y='TaxDistrict', orientation='h', title="Average Sale Price by Tax District", color='TaxDistrict')
    st.plotly_chart(fig_tax, use_container_width=True)

with row2_col2:
    fig_scatter = px.scatter(filtered_df, x='BuildingValue', y='SalePrice', color='Bedrooms', title="Building Value vs. Sale Price", opacity=0.6)
    st.plotly_chart(fig_scatter, use_container_width=True)

fig_box = px.box(filtered_df[filtered_df['Bedrooms'] <= 6], x='Bedrooms', y='SalePrice', title="Sale Price Variance by Bedroom Count", color='Bedrooms')
st.plotly_chart(fig_box, use_container_width=True)