# Olist Supply Chain Analytics

End-to-end supply chain analysis of **99,441 orders** from Olist, a Brazilian e-commerce marketplace: data exploration, SQL analytics, demand forecasting, inventory optimization and an interactive Streamlit dashboard.

**Tools:** Python (Pandas, Prophet, statsmodels), SQL (SQLite, window functions), Plotly, Streamlit

![Dashboard](images/dashboard.png)

## Business problem

As a supply chain analyst at Olist, the goal is to answer:

- Where are deliveries late, and which sellers drive poor customer experience?
- How much demand should we expect in the next 30/60/90 days?
- Which products matter most, and how much stock should we keep?

## Dataset

[Brazilian E-Commerce Public Dataset by Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): 9 tables covering orders, items, products, sellers, customers, payments and reviews (Sep 2016 – Oct 2018).

## Approach

| Phase | What was done | Skills |
|---|---|---|
| 1. Data exploration | Data quality checks, orders by state, top categories, delivery performance, seller scorecard | Pandas, EDA, data cleaning |
| 2. SQL analytics | 7-day moving average, month-over-month growth, seller ranking, declining categories, RFM segmentation, late delivery by region | CTEs, joins, `AVG() OVER`, `LAG()`, `RANK()`, `NTILE()` |
| 3. Demand forecasting | Prophet with event effects, fair comparison against 4 baseline methods, 30/60/90-day forecast | Time series, Prophet, MAPE, model selection |
| 4. Inventory optimization | ABC analysis, EOQ, safety stock and reorder points | Inventory formulas, segmentation |
| 5. Dashboard | Streamlit app with forecast, categories, seller scorecard, delivery by state and reorder plan | Streamlit, Plotly |

## Key insights

**Demand and customers**
- Demand is concentrated: **SP accounts for 42%** of orders and the top 3 states (SP, RJ, MG) for ~67%.
- **97% of customers ordered only once.** 22% are "at risk, high value" customers (avg spend R$298), so retention is the biggest growth opportunity.
- From Mar–May to Jun–Aug 2018, total orders fell 10%, but some categories fell **2.5–6x faster** (industry_commerce_and_business −61%, office_furniture −54%, cool_stuff −45%), signalling overstock risk.

**Delivery and sellers**
- **8.1% of deliveries were late**; average delivery time is 12.1 days.
- Northeast states have the highest late rates (**14–24%**, 19–25 days), vs **5.9%** in SP. By volume, SP and RJ have the most late orders.
- The lowest-rated sellers have **11–30% late delivery rates**, while top sellers are mostly at 0–3%: late delivery is a key driver of poor reviews.

**Forecasting**
- In a fair 8-week-ahead test, all methods scored 21–23.5% MAPE. **Prophet trained on 2018 data with a flat trend was best (21.4%, ~79% accuracy)**. Training on the full history did worst, because 2017's strong growth no longer applied: the training window mattered more than model complexity.

| Method (8-week-ahead, weekly) | MAPE |
|---|---|
| Prophet (2018 only, flat trend) | **21.4%** |
| Exponential smoothing | 21.7% |
| Naive (last known week) | 21.7% |
| 4-week average | 22.3% |
| Prophet (full history) | 23.5% |

- Forecast: **~234 orders/day**, ~7,000 in the next 30 days (range 5,600–8,500).
- Demand peaks Monday–Wednesday: **Monday needs ~55% more fulfilment capacity than Saturday**.

**Inventory**
- **27.7% of products generate 80% of revenue** (A class).
- Only **265 A products** have regular demand (≥1 unit every 10 days), yet they make up 24% of A-class revenue. EOQ and reorder points apply reliably to these; the rest are high-value, slow-moving items better handled with minimal stock or order-on-demand.

## Assumptions and limitations

- Olist has no inventory data, so EOQ and safety stock use stated assumptions: **lead time 7 days, ordering cost R$50, holding cost 25% of price per year, 95% service level**.
- Data covers less than 2 full years, so yearly seasonality isn't modelled; only weekly patterns and one-off events (Black Friday, Christmas, the May 2018 truck strike) are.
- The first and last months are incomplete, so forecasting uses Jan 2017 – 20 Aug 2018.
- Stockouts can't be measured directly; the `unavailable` order status is the closest proxy.

## Project structure

```
├── olist_supply_chain_analysis.ipynb   # Phases 1–4
├── app.py                              # Streamlit dashboard (Phase 5)
├── dashboard_data/                     # Results used by the dashboard
├── images/                             # Dashboard screenshots
└── requirements.txt
```

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

To re-run the notebook, download the dataset from Kaggle and place the CSV files in the project folder (also install `prophet` and `statsmodels`).

## Author

**Rahul Kumhar**, Supply Chain & Operations Analytics · [LinkedIn](https://www.linkedin.com/in/your-profile)
