# 3. E-commerce Customer Analytics (SQL / Python / Power BI)

Customer segmentation, repeat purchases, RFM analysis, retention, and revenue trends.

## Folder Structure
```
03_ecommerce_customers/
├── data/
│   ├── customers.csv            # 3,000 synthetic customers
│   ├── ecommerce_orders.csv     # ~15,900 orders (2024 - mid 2026)
│   └── rfm_output.csv           # generated after running analysis.py
├── sql/queries.sql              # 10 queries incl. full RFM segmentation
├── python/
│   ├── generate_data.py
│   └── analysis.py              # RFM + 5 charts
├── output/                      # Generated charts
└── README.md
```

## Dataset Columns
**customers.csv:** customer_id, city, signup_date, age, gender
**ecommerce_orders.csv:** order_id, customer_id, order_date, category, quantity,
unit_price, discount_pct, total_value, payment_mode, returned

## How to Use
1. `python3 python/generate_data.py` (optional, regenerates data)
2. `cd python && python3 analysis.py` → computes RFM scores, prints insights,
   saves `data/rfm_output.csv` and 5 charts to `output/`
3. **SQL:** load both CSVs as tables, run `sql/queries.sql` (includes a full
   NTILE-based RFM segmentation query)
4. **Power BI:** import both CSVs, relate on `customer_id`. Suggested visuals:
   - Bar: customers per RFM segment
   - Line: monthly revenue trend
   - Bar: revenue by category
   - Scatter: frequency vs monetary by segment
   - KPI cards: repeat purchase rate, AOV, total revenue

## Key Insight Areas Covered
- RFM segmentation (Champions, Loyal, Potential Loyalists, At Risk, Lost)
- Repeat purchase rate
- Revenue & order trends by month/category/city
- Return rate by category
- Payment mode preference
