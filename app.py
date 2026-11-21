"""
Olist Supply Chain Dashboard
Run with:  streamlit run app.py
Reads the CSV files saved from the notebook in the 'dashboard_data' folder.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Olist Supply Chain Dashboard", layout="wide")

## ---------- Colours (one palette used across every chart) ----------
INK, MUTED, TEAL, TEAL_LIGHT, AMBER = "#1B2A35", "#6B7A86", "#0F766E", "#99D5CF", "#D97706"

st.markdown(f"""
<style>
  h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}
  [data-testid="stMetricValue"] {{ color: {TEAL}; }}
  [data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
</style>
""", unsafe_allow_html=True)

DATA = "dashboard_data"

## ---------- Load data once and cache it (faster reloads) ----------
@st.cache_data
def load():
    daily = pd.read_csv(f"{DATA}/daily_orders.csv", parse_dates=["ds"])
    fc = pd.read_csv(f"{DATA}/forecast_90d.csv", parse_dates=["ds"])
    cats = pd.read_csv(f"{DATA}/top_categories.csv")
    cats.columns = ["category", "items"]                      # first column is the category name
    sellers = pd.read_csv(f"{DATA}/seller_performance.csv")
    states = pd.read_csv(f"{DATA}/state_delivery.csv")
    inv = pd.read_csv(f"{DATA}/inventory_regular_A.csv")
    return daily, fc, cats, sellers, states, inv

daily, fc, cats, sellers, states, inv = load()

## ---------- Header with the four numbers a planner checks first ----------
st.title("Olist supply chain dashboard")
st.caption("Brazilian e-commerce orders, Jan 2017 – Aug 2018 · forecast, delivery, seller and inventory view")

delivered = states["orders"].sum()
late_overall = (states["late_pct"] * states["orders"]).sum() / delivered     # weighted by orders
c1, c2, c3, c4 = st.columns(4)
c1.metric("Forecast, next 30 days", f"{fc.head(30)['yhat'].sum():,.0f} orders",
          f"~{fc.head(30)['yhat'].mean():.0f} per day", delta_color="off")
c2.metric("Late deliveries", f"{late_overall:.1f}%", "of delivered orders", delta_color="off")
c3.metric("Sellers tracked", f"{len(sellers):,}", "with 30+ orders", delta_color="off")
c4.metric("Regular A products", f"{len(inv):,}", "with reorder points", delta_color="off")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Demand forecast", "Categories", "Sellers", "Delivery by state", "Inventory"])

## ---------- 1. Demand forecast ----------
with tab1:
    recent = daily[daily["ds"] >= daily["ds"].max() - pd.Timedelta(days=120)]   # last 120 days of actuals
    fig = go.Figure()
    ## Shaded band = likely range (yhat_lower to yhat_upper)
    fig.add_trace(go.Scatter(x=pd.concat([fc["ds"], fc["ds"][::-1]]),
                             y=pd.concat([fc["yhat_upper"], fc["yhat_lower"][::-1]]),
                             fill="toself", fillcolor="rgba(15,118,110,0.15)", line=dict(width=0),
                             name="Likely range", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=recent["ds"], y=recent["y"], name="Actual orders",
                             line=dict(color=INK, width=1.5)))
    fig.add_trace(go.Scatter(x=fc["ds"], y=fc["yhat"], name="Forecast",
                             line=dict(color=TEAL, width=2.5)))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10),
                      yaxis_title="Orders per day", legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns([1, 1.4])
    with left:
        st.subheader("Expected orders")
        totals = pd.DataFrame({
            "Horizon": ["Next 30 days", "Next 60 days", "Next 90 days"],
            "Forecast": [fc.head(d)["yhat"].sum() for d in (30, 60, 90)],
            "Low": [fc.head(d)["yhat_lower"].sum() for d in (30, 60, 90)],
            "High": [fc.head(d)["yhat_upper"].sum() for d in (30, 60, 90)],
        }).round(0)
        st.dataframe(totals.style.format({"Forecast": "{:,.0f}", "Low": "{:,.0f}", "High": "{:,.0f}"}),
                     hide_index=True, width="stretch")
        st.caption("Model: Prophet on 2018 data, flat trend, ~79% weekly accuracy (MAPE 21.4%).")
    with right:
        st.subheader("Average forecast by weekday")
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        wd = (fc.assign(day=fc["ds"].dt.day_name()).groupby("day")["yhat"].mean()
              .reindex(order).reset_index())
        fig = px.bar(wd, x="day", y="yhat", labels={"day": "", "yhat": "Orders per day"},
                     color_discrete_sequence=[TEAL])
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption("Monday needs ~55% more fulfilment capacity than Saturday.")

## ---------- 2. Top categories ----------
with tab2:
    st.subheader("Top categories by items sold")
    fig = px.bar(cats.sort_values("items"), x="items", y="category", orientation="h",
                 labels={"items": "Items sold", "category": ""}, color_discrete_sequence=[TEAL])
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("Home categories (bed_bath_table, furniture_decor, housewares) lead demand.")

## ---------- 3. Seller scorecard ----------
with tab3:
    st.subheader("Seller scorecard")
    min_orders = st.slider("Minimum orders per seller", 30, 300, 30, step=10)
    s = sellers[sellers["orders"] >= min_orders]
    ## Each dot = one seller; late sellers to the right tend to have lower reviews
    fig = px.scatter(s, x="late_pct", y="avg_review", size="orders", hover_data=["seller_id"],
                     labels={"late_pct": "Late deliveries (%)", "avg_review": "Average review"},
                     color_discrete_sequence=[TEAL], opacity=0.6)
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")

    best, worst = st.columns(2)
    cols = ["seller_id", "orders", "late_pct", "avg_review"]
    best.markdown("**Best rated**")
    best.dataframe(s.sort_values(["avg_review", "late_pct"], ascending=[False, True])[cols].head(10),
                   hide_index=True, width="stretch")
    worst.markdown("**Lowest rated**")
    worst.dataframe(s.sort_values(["avg_review", "late_pct"], ascending=[True, False])[cols].head(10),
                    hide_index=True, width="stretch")

## ---------- 4. Delivery by state ----------
with tab4:
    st.subheader("Late delivery by customer state")
    st_min = st.slider("Minimum delivered orders per state", 0, 2000, 300, step=100)
    d = states[states["orders"] >= st_min].sort_values("late_pct")
    ## Bar colour shows average delivery days: darker = slower
    fig = px.bar(d, x="late_pct", y="state", orientation="h", color="avg_days",
                 color_continuous_scale=[TEAL_LIGHT, TEAL, AMBER],
                 labels={"late_pct": "Late deliveries (%)", "state": "", "avg_days": "Avg days"},
                 hover_data=["orders"])
    fig.update_layout(height=600, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("Northeast states have the highest late rates; SP and RJ have the most late orders by volume.")

## ---------- 5. Inventory recommendations ----------
with tab5:
    st.subheader("Reorder plan for regular A-class products")
    st.caption("Assumptions: lead time 7 days · ordering cost R$50 · holding cost 25% of price per year · "
               "95% service level. Applies to products selling at least 1 unit every 10 days.")
    search = st.text_input("Find a product ID")
    view = inv[inv["product_id"].str.contains(search.strip(), case=False)] if search else inv
    show = (view.sort_values("revenue", ascending=False)
            [["product_id", "avg_daily", "avg_price", "eoq", "safety_stock", "reorder_point", "revenue"]]
            .rename(columns={"avg_daily": "Units/day", "avg_price": "Price (R$)", "eoq": "Order qty (EOQ)",
                             "safety_stock": "Safety stock", "reorder_point": "Reorder at",
                             "revenue": "Revenue (R$)"}))
    st.dataframe(show.style.format({"Units/day": "{:.2f}", "Price (R$)": "{:,.0f}",
                                    "Order qty (EOQ)": "{:.0f}", "Safety stock": "{:.0f}",
                                    "Reorder at": "{:.0f}", "Revenue (R$)": "{:,.0f}"}),
                 hide_index=True, width="stretch", height=460)
    st.download_button("Download reorder plan (CSV)", show.to_csv(index=False),
                       file_name="reorder_plan_regular_A.csv")
