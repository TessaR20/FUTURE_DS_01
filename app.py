"""
Sales Performance Dashboard
----------------------------
Interactive analytics dashboard for a multi-category retail/e-commerce business.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Expects a CSV in the same folder named `sales_data.csv` with columns:
Order ID, Order Date, Category, Product, Region, City, Customer Segment,
Sales Channel, Quantity, Unit Price, Gross Sales, Discount %, Discount Amount,
Net Sales, Profit
(If the file isn't found, you'll be prompted to upload one with the same structure.)
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#2E5EAA"
TEAL = "#1B998B"
ORANGE = "#F0913B"
PINK = "#C94277"
PURPLE = "#6C63A5"
PALETTE = [PRIMARY, TEAL, ORANGE, PINK, PURPLE]

CUSTOM_CSS = """
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {
    background-color: #F5F7FA;
    border: 1px solid #E3E8EF;
    border-radius: 10px;
    padding: 14px 16px 10px 16px;
}
[data-testid="stMetricLabel"] { font-size: 0.8rem; color: #595959; }
[data-testid="stMetricValue"] { font-size: 1.55rem; color: #1F3864; }
h1, h2, h3 { color: #1F3864; }
.stTabs [data-baseweb="tab-list"] { display: flex; justify-content: space-evenly; gap: 0.35rem; }
.stTabs [data-baseweb="tab"] { font-size: 0.95rem; flex: 1 1 0; justify-content: center; text-align: center; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path_or_buffer):
    df = pd.read_csv(path_or_buffer, parse_dates=["Order Date"])
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Year"] = df["Order Date"].dt.year
    df["Weekday"] = df["Order Date"].dt.day_name()
    return df


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "sales_data.csv")

if os.path.exists(DEFAULT_PATH):
    df_raw = load_data(DEFAULT_PATH)
else:
    st.title("Sales Performance Dashboard")
    st.info("No `sales_data.csv` found next to this script. Upload a CSV with the expected columns to continue.")
    uploaded = st.file_uploader("Upload sales data (CSV)", type=["csv"])
    if uploaded is None:
        st.stop()
    df_raw = load_data(uploaded)

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.title("Sales Dashboard")
st.sidebar.caption("Filter the data below — all charts and KPIs update live.")

min_date, max_date = df_raw["Order Date"].min().date(), df_raw["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

categories = st.sidebar.multiselect(
    "Category", sorted(df_raw["Category"].unique()), default=sorted(df_raw["Category"].unique())
)
regions = st.sidebar.multiselect(
    "Region", sorted(df_raw["Region"].unique()), default=sorted(df_raw["Region"].unique())
)
channels = st.sidebar.multiselect(
    "Sales Channel", sorted(df_raw["Sales Channel"].unique()), default=sorted(df_raw["Sales Channel"].unique())
)
segments = st.sidebar.multiselect(
    "Customer Segment", sorted(df_raw["Customer Segment"].unique()), default=sorted(df_raw["Customer Segment"].unique())
)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit + Plotly")

# ----------------------------------------------------------------------------
# Apply filters
# ----------------------------------------------------------------------------
mask = (
    (df_raw["Order Date"].dt.date >= start_date)
    & (df_raw["Order Date"].dt.date <= end_date)
    & (df_raw["Category"].isin(categories))
    & (df_raw["Region"].isin(regions))
    & (df_raw["Sales Channel"].isin(channels))
    & (df_raw["Customer Segment"].isin(segments))
)
df = df_raw.loc[mask].copy()

if df.empty:
    st.warning("No data matches the current filters. Adjust the filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------------
st.title("Sales Performance Dashboard")
st.caption(f"Showing {len(df):,} order line items from {start_date} to {end_date}")

total_sales = df["Net Sales"].sum()
total_profit = df["Profit"].sum()
margin = total_profit / total_sales if total_sales else 0
n_orders = df["Order ID"].nunique()
aov = df.groupby("Order ID")["Net Sales"].sum().mean()

# YoY comparison (based on full-year data available in the filtered set, if any)
years = sorted(df["Year"].unique())
yoy_txt = None
if len(years) >= 2:
    prev_y, last_y = years[-2], years[-1]
    prev_sales = df[df.Year == prev_y]["Net Sales"].sum()
    last_sales = df[df.Year == last_y]["Net Sales"].sum()
    if prev_sales:
        yoy = (last_sales - prev_sales) / prev_sales
        yoy_txt = f"{yoy:+.1%} vs {prev_y}"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Net Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Profit Margin", f"{margin:.1%}")
k4.metric("Orders", f"{n_orders:,}")
k5.metric("Avg Order Value", f"${aov:,.2f}", yoy_txt)

st.markdown("---")

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tab_trend, tab_products, tab_category, tab_region, tab_channel, tab_data = st.tabs(
    ["Trend", "Top Products", "Category", "Region", "Channel", "Raw Data"]
)

# ---- Trend tab ----
with tab_trend:
    c1, c2 = st.columns([2, 1])
    with c1:
        gran = st.radio("Granularity", ["Monthly", "Weekly", "Daily"], horizontal=True)
        freq_map = {"Monthly": "ME", "Weekly": "W", "Daily": "D"}
        trend = (
            df.set_index("Order Date")
            .resample(freq_map[gran])["Net Sales"]
            .sum()
            .reset_index()
        )
        fig = px.area(trend, x="Order Date", y="Net Sales", markers=(gran != "Daily"))
        fig.update_traces(line_color=PRIMARY, fillcolor="rgba(46,94,170,0.12)")
        fig.update_layout(
            title=f"{gran} Revenue Trend", yaxis_title="Net Sales ($)", xaxis_title="",
            hovermode="x unified", margin=dict(t=50, l=10, r=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        profit_trend = (
            df.set_index("Order Date").resample(freq_map[gran])[["Net Sales", "Profit"]].sum().reset_index()
        )
        profit_trend["Margin"] = profit_trend["Profit"] / profit_trend["Net Sales"]
        fig2 = px.line(profit_trend, x="Order Date", y="Margin")
        fig2.update_traces(line_color=ORANGE)
        fig2.update_layout(
            title="Profit Margin Over Time", yaxis_tickformat=".0%", xaxis_title="",
            margin=dict(t=50, l=10, r=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Sales by day of week**")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df.groupby("Weekday")["Net Sales"].sum().reindex(dow_order).reset_index()
    fig3 = px.bar(dow, x="Weekday", y="Net Sales", color_discrete_sequence=[TEAL])
    fig3.update_layout(margin=dict(t=10, l=10, r=10, b=10), yaxis_title="Net Sales ($)")
    st.plotly_chart(fig3, use_container_width=True)

# ---- Top products tab ----
with tab_products:
    top_n = st.slider("Number of products to show", 5, 25, 10)
    prod = (
        df.groupby("Product")
        .agg(Net_Sales=("Net Sales", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum"))
        .sort_values("Net_Sales", ascending=False)
        .head(top_n)
        .reset_index()
    )
    fig = px.bar(
        prod.sort_values("Net_Sales"), x="Net_Sales", y="Product", orientation="h",
        color_discrete_sequence=[PRIMARY], text="Net_Sales",
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(title=f"Top {top_n} Products by Revenue", xaxis_title="Net Sales ($)",
                       margin=dict(t=50, l=10, r=10, b=10), height=max(350, top_n * 30))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        prod.style.format({"Net_Sales": "${:,.0f}", "Profit": "${:,.0f}", "Units": "{:,.0f}"}),
        use_container_width=True, hide_index=True,
    )

# ---- Category tab ----
with tab_category:
    cat = (
        df.groupby("Category")
        .agg(Net_Sales=("Net Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
    )
    cat["Margin"] = cat["Profit"] / cat["Net_Sales"]
    cat = cat.sort_values("Net_Sales", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_bar(name="Net Sales", x=cat["Category"], y=cat["Net_Sales"], marker_color=PRIMARY)
        fig.add_bar(name="Profit", x=cat["Category"], y=cat["Profit"], marker_color=TEAL)
        fig.update_layout(title="Revenue & Profit by Category", barmode="group",
                           margin=dict(t=50, l=10, r=10, b=10), yaxis_title="$")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(
            cat.sort_values("Margin"), x="Margin", y="Category", orientation="h",
            color_discrete_sequence=[ORANGE], text="Margin",
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_layout(title="Profit Margin by Category", xaxis_tickformat=".0%",
                           margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Category × Region heatmap (Net Sales)**")
    pivot = df.pivot_table(index="Category", columns="Region", values="Net Sales", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=".2s", color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ---- Region tab ----
with tab_region:
    reg = df.groupby("Region")["Net Sales"].sum().reset_index().sort_values("Net Sales", ascending=False)
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = px.pie(reg, names="Region", values="Net Sales", hole=0.45, color_discrete_sequence=PALETTE)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(title="Revenue Share by Region", margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        city = df.groupby(["Region", "City"])["Net Sales"].sum().reset_index().sort_values("Net Sales", ascending=False)
        fig = px.bar(city, x="Net Sales", y="City", color="Region", orientation="h",
                      color_discrete_sequence=PALETTE)
        fig.update_layout(title="Revenue by City", margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

# ---- Channel tab ----
with tab_channel:
    chan = df.groupby("Sales Channel").agg(Net_Sales=("Net Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(chan.sort_values("Net_Sales", ascending=False), x="Sales Channel", y="Net_Sales",
                      color="Sales Channel", color_discrete_sequence=PALETTE, text="Net_Sales")
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(title="Revenue by Channel", showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        seg = df.groupby(["Sales Channel", "Customer Segment"])["Net Sales"].sum().reset_index()
        fig = px.bar(seg, x="Sales Channel", y="Net Sales", color="Customer Segment", barmode="stack",
                      color_discrete_sequence=PALETTE)
        fig.update_layout(title="Channel × Customer Segment", margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

# ---- Raw data tab ----
with tab_data:
    st.markdown(f"**{len(df):,} rows** match the current filters.")
    st.dataframe(df.drop(columns=["Month", "Year", "Weekday"]), use_container_width=True, height=450)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_sales_data.csv", "text/csv")
