"""
E-commerce Customer Analytics: RFM segmentation, repeat purchase, retention, revenue trend
Run: python3 analysis.py
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

DATA_DIR = "../data"
OUT_DIR = "../output"

orders = pd.read_csv(f"{DATA_DIR}/ecommerce_orders.csv", parse_dates=["order_date"])
customers = pd.read_csv(f"{DATA_DIR}/customers.csv", parse_dates=["signup_date"])

ANALYSIS_DATE = datetime(2026, 7, 1)

print("="*60)
print("E-COMMERCE CUSTOMER ANALYTICS SUMMARY")
print("="*60)

print(f"\nTotal Orders: {orders['order_id'].nunique()}")
print(f"Total Customers: {orders['customer_id'].nunique()}")
print(f"Total Revenue: INR {orders['total_value'].sum():,.2f}")
print(f"Avg Order Value: INR {orders['total_value'].mean():,.2f}")

# ---- RFM ----
rfm = orders.groupby("customer_id").agg(
    last_order_date=("order_date", "max"),
    frequency=("order_id", "count"),
    monetary=("total_value", "sum"),
).reset_index()
rfm["recency_days"] = (ANALYSIS_DATE - rfm["last_order_date"]).dt.days

rfm["r_score"] = pd.qcut(rfm["recency_days"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

def segment(score):
    if score >= 10:
        return "Champions"
    elif score >= 8:
        return "Loyal Customers"
    elif score >= 6:
        return "Potential Loyalists"
    elif score >= 4:
        return "At Risk"
    else:
        return "Lost / Churned"

rfm["segment"] = rfm["rfm_total"].apply(segment)
rfm.to_csv(f"{DATA_DIR}/rfm_output.csv", index=False)

print("\n--- Customer Segments (RFM) ---")
print(rfm["segment"].value_counts())

# Repeat purchase rate
repeat_rate = (rfm["frequency"] > 1).mean() * 100
print(f"\nRepeat Purchase Rate: {repeat_rate:.2f}%")

# Revenue by category
print("\n--- Revenue by Category ---")
print(orders.groupby("category")["total_value"].sum().sort_values(ascending=False).round(2))

# Return rate by category
print("\n--- Return Rate by Category (%) ---")
print((orders.groupby("category")["returned"].mean() * 100).round(2).sort_values(ascending=False))

# ---------------- CHARTS ----------------
plt.style.use("seaborn-v0_8-whitegrid")

# Chart 1: Customer segments
plt.figure(figsize=(8, 6))
rfm["segment"].value_counts().plot(kind="bar", color="#3b82f6")
plt.title("Customer Segments (RFM Analysis)")
plt.ylabel("Number of Customers")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/rfm_segments.png", dpi=150)
plt.close()

# Chart 2: Monthly revenue trend
monthly_rev = orders.groupby(orders["order_date"].dt.to_period("M"))["total_value"].sum()
plt.figure(figsize=(12, 5))
monthly_rev.plot(kind="line", marker="o", color="#0ea5e9")
plt.title("Monthly Revenue Trend")
plt.ylabel("Revenue (INR)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/monthly_revenue.png", dpi=150)
plt.close()

# Chart 3: Revenue by category
plt.figure(figsize=(9, 5))
orders.groupby("category")["total_value"].sum().sort_values().plot(kind="barh", color="#8b5cf6")
plt.title("Revenue by Category")
plt.xlabel("Revenue (INR)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/revenue_by_category.png", dpi=150)
plt.close()

# Chart 4: RFM scatter (Frequency vs Monetary, colored by segment)
plt.figure(figsize=(9, 6))
segments = rfm["segment"].unique()
colors = plt.cm.tab10.colors
for i, seg in enumerate(segments):
    subset = rfm[rfm["segment"] == seg]
    plt.scatter(subset["frequency"], subset["monetary"], label=seg, alpha=0.6, color=colors[i % 10])
plt.title("Customer Frequency vs Monetary Value by Segment")
plt.xlabel("Frequency (Order Count)")
plt.ylabel("Monetary Value (INR)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/rfm_scatter.png", dpi=150)
plt.close()

# Chart 5: Payment mode share
plt.figure(figsize=(6, 6))
orders["payment_mode"].value_counts().plot(kind="pie", autopct="%1.1f%%")
plt.title("Payment Mode Share")
plt.ylabel("")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/payment_mode_share.png", dpi=150)
plt.close()

print("\nCharts saved to output/ folder. RFM table saved to data/rfm_output.csv")
