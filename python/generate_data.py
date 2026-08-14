"""
Generates synthetic E-commerce orders dataset for customer analytics (RFM, retention, revenue).
Output: ../data/ecommerce_orders.csv, ../data/customers.csv
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(21)

N_CUSTOMERS = 3000
N_ORDERS = 25000

cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"]
categories = ["Electronics", "Fashion", "Home & Kitchen", "Beauty", "Books", "Sports", "Grocery", "Toys"]
payment_modes = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]

# Customers
customer_ids = [f"CUST{5000+i}" for i in range(N_CUSTOMERS)]
signup_start = datetime(2023, 1, 1)
signup_end = datetime(2025, 12, 31)
signup_range = (signup_end - signup_start).days

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "city": np.random.choice(cities, N_CUSTOMERS),
    "signup_date": [
        (signup_start + timedelta(days=int(np.random.randint(0, signup_range + 1)))).strftime("%Y-%m-%d")
        for _ in range(N_CUSTOMERS)
    ],
    "age": np.random.randint(18, 60, N_CUSTOMERS),
    "gender": np.random.choice(["Male", "Female"], N_CUSTOMERS, p=[0.52, 0.48]),
})
customers.to_csv("/home/claude/projects/03_ecommerce_customers/data/customers.csv", index=False)

# Give each customer a "loyalty" factor -> affects order frequency & value
loyalty = np.random.beta(2, 5, N_CUSTOMERS)  # skewed towards lower loyalty (most customers order less)

order_start = datetime(2024, 1, 1)
order_end = datetime(2026, 6, 30)
order_range_days = (order_end - order_start).days

rows = []
order_id = 900000
for idx, cust in enumerate(customer_ids):
    # number of orders for this customer, driven by loyalty factor
    n_orders_cust = max(1, int(np.random.poisson(1 + loyalty[idx] * 15)))
    for _ in range(n_orders_cust):
        order_id += 1
        day_offset = np.random.randint(0, order_range_days + 1)
        order_date = order_start + timedelta(days=day_offset)
        category = np.random.choice(categories)
        quantity = np.random.randint(1, 5)
        unit_price = round(np.random.uniform(150, 8000), 2)
        total_value = round(unit_price * quantity, 2)
        discount_pct = np.random.choice([0, 5, 10, 15, 20], p=[0.4, 0.2, 0.2, 0.15, 0.05])
        payment = np.random.choice(payment_modes, p=[0.4, 0.25, 0.15, 0.1, 0.1])
        returned = np.random.choice([0, 1], p=[0.92, 0.08])

        rows.append({
            "order_id": f"ORD{order_id}",
            "customer_id": cust,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_pct": discount_pct,
            "total_value": round(total_value * (1 - discount_pct/100), 2),
            "payment_mode": payment,
            "returned": returned,
        })

    if len(rows) >= N_ORDERS:
        break

orders = pd.DataFrame(rows)
orders.to_csv("/home/claude/projects/03_ecommerce_customers/data/ecommerce_orders.csv", index=False)
print("Generated", len(customers), "customers and", len(orders), "orders")
print(orders.head())
