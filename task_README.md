# Sales Performance Analysis — Simulated Multi-Category Retail Business

Client-ready sales analysis built as part of a data analytics internship task. Simulates
a 2-year (Jan 2024–Dec 2025) transaction history for a multi-category retail/e-commerce
business, then analyzes trends, top products, category/region/channel performance, and
delivers a formal report with insights and recommendations.

## 📁 Contents

| File | Description |
|---|---|
| `sales_data.csv` | Raw simulated dataset — 12,180 order line items (Order ID, Date, Category, Product, Region, City, Segment, Channel, Quantity, Pricing, Discounts, Net Sales, Profit) |
| `Sales_Performance_Report.docx` | Full client-ready report: KPIs, trend analysis, top products, category/region/channel breakdown, and actionable recommendations |
| `charts/` | All charts used in the report, exported as standalone PNGs |
| `dashboard/app.py` | Interactive Python (Streamlit + Plotly) dashboard — filter by date, category, region, channel, segment; live KPIs, trend/product/category/region/channel views, raw-data export |
| `dashboard/requirements.txt` | Python dependencies for the dashboard |

## 📊 Key Findings

- **Total Net Sales (2024–2025):** $1,518,360 | **Total Profit:** $499,230 (32.9% margin)
- **YoY Growth:** Revenue grew **17.0%** from 2024 to 2025
- **Seasonality:** Nov–Dec is the strongest period of the year (~35–45% above average month); Jan–Feb is consistently the softest
- **Top category by revenue:** Sports & Outdoors | **Highest-margin category:** Apparel (~45%)
- **Top channel:** Online (~55% of total revenue) — more than double Retail Store and Marketplace combined
- **Regional footprint:** Well diversified — no region varies more than ~6% from the average

## 🎯 Top Recommendations

1. Shift marketing/inventory investment toward Q4 to capture the proven seasonal peak
2. Expand the Apparel line — it converts revenue to profit most efficiently
3. Review Electronics discounting/pricing — strong volume but the thinnest margin
4. Prioritize continued investment in the Online channel
5. Use the Jan–Feb lull for clearance campaigns and supplier renegotiation
6. Audit the Marketplace channel to decide whether to scale or deprioritize it

## 🚀 Running the Dashboard

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

The app looks for `sales_data.csv` in the same folder (already included). It opens in your
browser at `http://localhost:8501` with sidebar filters (date range, category, region,
channel, customer segment) and six tabs: Trend, Top Products, Category, Region, Channel,
and Raw Data (with CSV export of the filtered view).

## 🛠️ Methodology & Tools

- **Data generation:** Python (pandas, numpy) — simulated realistic seasonality, weekday
  effects, discounting behavior, and year-over-year growth across 5 categories, 4 regions,
  and 3 sales channels
- **Analysis & visualization:** Python (pandas, matplotlib)
- **Report:** Generated as a formatted Word document (docx)

To reproduce or adapt this analysis for a real dataset, replace `sales_data.csv` with a
client's transaction export (mapped to the same column structure) and re-run the analysis
scripts — no other changes required.

## 📌 About This Project

Built as a self-directed "act like a real analyst" exercise: rather than relying only on a
downloaded Kaggle dataset, this project simulates a plausible small-to-mid-size retail
business so the workflow — data generation/cleaning, KPI definition, trend analysis, and
client-facing storytelling — mirrors what a freelance analyst would actually deliver.
