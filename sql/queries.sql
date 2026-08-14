-- ============================================================
-- E-commerce Customer Analytics - SQL Queries
-- Tables: customers (customer_id, city, signup_date, age, gender)
--         ecommerce_orders (order_id, customer_id, order_date, category,
--                            quantity, unit_price, discount_pct, total_value,
--                            payment_mode, returned)
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id  VARCHAR(20),
    city         VARCHAR(30),
    signup_date  DATE,
    age          INT,
    gender       VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS ecommerce_orders (
    order_id      VARCHAR(20),
    customer_id   VARCHAR(20),
    order_date    DATE,
    category      VARCHAR(30),
    quantity      INT,
    unit_price    DECIMAL(10,2),
    discount_pct  INT,
    total_value   DECIMAL(12,2),
    payment_mode  VARCHAR(30),
    returned      INT
);

-- 1. Total revenue, orders, avg order value
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(total_value), 2) AS total_revenue,
    ROUND(AVG(total_value), 2) AS avg_order_value
FROM ecommerce_orders;

-- 2. RFM base metrics per customer
-- (Recency = days since last order from a fixed "analysis_date")
SELECT
    customer_id,
    MAX(order_date) AS last_order_date,
    JULIANDAY('2026-07-01') - JULIANDAY(MAX(order_date)) AS recency_days,  -- SQLite; use DATEDIFF in MySQL
    COUNT(order_id) AS frequency,
    ROUND(SUM(total_value), 2) AS monetary
FROM ecommerce_orders
GROUP BY customer_id;

-- 3. RFM Segmentation using NTILE (quartile scoring, Postgres/MySQL 8+/SQLite)
WITH rfm_base AS (
    SELECT
        customer_id,
        JULIANDAY('2026-07-01') - JULIANDAY(MAX(order_date)) AS recency_days,
        COUNT(order_id) AS frequency,
        SUM(total_value) AS monetary
    FROM ecommerce_orders
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id, recency_days, frequency, monetary,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,   -- lower recency_days = more recent = higher score
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_base
)
SELECT
    customer_id, recency_days, frequency, monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 8  THEN 'Loyal Customers'
        WHEN (r_score + f_score + m_score) >= 6  THEN 'Potential Loyalists'
        WHEN (r_score + f_score + m_score) >= 4  THEN 'At Risk'
        ELSE 'Lost / Churned'
    END AS customer_segment
FROM rfm_scores
ORDER BY rfm_total DESC;

-- 4. Repeat purchase rate
SELECT
    ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_purchase_rate_pct
FROM (
    SELECT customer_id, COUNT(order_id) AS order_count
    FROM ecommerce_orders
    GROUP BY customer_id
) t;

-- 5. Monthly revenue trend
SELECT
    STRFTIME('%Y-%m', order_date) AS month,
    COUNT(order_id) AS orders,
    ROUND(SUM(total_value), 2) AS revenue
FROM ecommerce_orders
GROUP BY month
ORDER BY month;

-- 6. Revenue by category
SELECT category, COUNT(*) AS orders, ROUND(SUM(total_value),2) AS revenue
FROM ecommerce_orders
GROUP BY category
ORDER BY revenue DESC;

-- 7. Revenue by city (join with customers)
SELECT c.city, ROUND(SUM(o.total_value),2) AS revenue, COUNT(DISTINCT o.customer_id) AS customers
FROM ecommerce_orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
ORDER BY revenue DESC;

-- 8. Return rate by category
SELECT category,
       COUNT(*) AS total_orders,
       SUM(returned) AS returned_orders,
       ROUND(100.0 * SUM(returned) / COUNT(*), 2) AS return_rate_pct
FROM ecommerce_orders
GROUP BY category
ORDER BY return_rate_pct DESC;

-- 9. Payment mode preference
SELECT payment_mode, COUNT(*) AS orders, ROUND(SUM(total_value),2) AS revenue
FROM ecommerce_orders
GROUP BY payment_mode
ORDER BY orders DESC;

-- 10. Cohort retention (signup month -> active months) - simplified monthly cohort
SELECT
    STRFTIME('%Y-%m', c.signup_date) AS signup_month,
    STRFTIME('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.customer_id) AS active_customers
FROM ecommerce_orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY signup_month, order_month
ORDER BY signup_month, order_month;
