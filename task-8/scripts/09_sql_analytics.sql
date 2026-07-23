-- Olist E-commerce SQL Analytics Suite
-- Note: Date parsing uses SUBSTR() on ISO datetime strings for maximum cross-compatibility between MySQL and SQLite.

-- Q1: What are the total overall sales (revenue)?
SELECT ROUND(SUM(price), 2) AS total_revenue 
FROM order_items;

-- Q2: What are the total sales per month?
SELECT SUBSTR(o.order_purchase_timestamp, 1, 7) AS purchase_month, 
       ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY purchase_month
ORDER BY purchase_month;

-- Q3: What are the total sales per year?
SELECT SUBSTR(o.order_purchase_timestamp, 1, 4) AS purchase_year, 
       ROUND(SUM(oi.price), 2) AS yearly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY purchase_year
ORDER BY purchase_year;

-- Q4: What is the Customer Lifetime Value (CLV) for the top 10 customers?
SELECT c.customer_unique_id, 
       ROUND(SUM(oi.price), 2) AS clv
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_unique_id
ORDER BY clv DESC
LIMIT 10;

-- Q5: What is the best-selling product by revenue?
SELECT p.product_id, 
       p.product_category_name, 
       ROUND(SUM(oi.price), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY total_revenue DESC
LIMIT 1;

-- Q6: What is the worst-selling product by revenue?
SELECT p.product_id, 
       p.product_category_name, 
       ROUND(SUM(oi.price), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY total_revenue ASC
LIMIT 1;

-- Q7: What is the best-selling product by units sold?
SELECT p.product_id, 
       p.product_category_name, 
       COUNT(oi.order_item_id) AS units_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY units_sold DESC
LIMIT 1;

-- Q8: What is the worst-selling product by units sold?
SELECT p.product_id, 
       p.product_category_name, 
       COUNT(oi.order_item_id) AS units_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY units_sold ASC
LIMIT 1;

-- Q9: What is the total revenue by product category?
SELECT p.product_category_name, 
       ROUND(SUM(oi.price), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_category_name
ORDER BY total_revenue DESC;

-- Q10: What is the total revenue by customer city?
SELECT c.customer_city, 
       ROUND(SUM(oi.price), 2) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_city
ORDER BY total_revenue DESC
LIMIT 20;

-- Q11: What is the total revenue by customer state?
SELECT c.customer_state, 
       ROUND(SUM(oi.price), 2) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC;

-- Q12: Who are the top 10 customers by spend? (Identical logic to Q4, but explicitly checking order_id combinations if requested, we use total spend)
SELECT c.customer_unique_id, 
       COUNT(DISTINCT o.order_id) AS total_orders,
       ROUND(SUM(oi.price), 2) AS total_spend
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_unique_id
ORDER BY total_spend DESC
LIMIT 10;

-- Q13: How many repeat customers are there (customers with >1 order)?
SELECT COUNT(*) AS repeat_customer_count
FROM (
    SELECT c.customer_unique_id
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
    HAVING COUNT(DISTINCT o.order_id) > 1
) AS repeat_customers;

-- Q14: What percentage of total revenue comes from repeat customers?
WITH RepeatCust AS (
    SELECT c.customer_unique_id
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
    HAVING COUNT(DISTINCT o.order_id) > 1
),
RevenueCalc AS (
    SELECT 
        SUM(CASE WHEN c.customer_unique_id IN (SELECT customer_unique_id FROM RepeatCust) THEN oi.price ELSE 0 END) AS repeat_revenue,
        SUM(oi.price) AS total_revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
)
SELECT 
    ROUND(repeat_revenue, 2) AS repeat_revenue,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND((repeat_revenue / total_revenue) * 100, 2) AS repeat_revenue_percentage
FROM RevenueCalc;

-- Q15: What is the total revenue by payment method?
-- Note: Payment value might include freight, so we sum payment_value directly from payments table
SELECT payment_type, 
       ROUND(SUM(payment_value), 2) AS total_payment_revenue
FROM payments
GROUP BY payment_type
ORDER BY total_payment_revenue DESC;

-- Q16: What is the Average Order Value (AOV) overall?
SELECT ROUND(SUM(price) / COUNT(DISTINCT order_id), 2) AS overall_aov
FROM order_items;

-- Q17: What is the Average Order Value (AOV) by state?
SELECT c.customer_state, 
       ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS state_aov
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY state_aov DESC;

-- Q18: Which month/year had the highest revenue?
SELECT SUBSTR(o.order_purchase_timestamp, 1, 7) AS highest_revenue_month, 
       ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY highest_revenue_month
ORDER BY monthly_revenue DESC
LIMIT 1;

-- Q19: Which products were never sold? (Products with zero order_items)
SELECT p.product_id, p.product_category_name
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;

-- Q20: Are there any customers registered who have no orders?
SELECT c.customer_unique_id
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Q21: What is the average revenue by review score?
SELECT r.review_score, 
       ROUND(AVG(OrderRev.order_revenue), 2) AS avg_revenue_per_order
FROM reviews r
JOIN (
    SELECT order_id, SUM(price) AS order_revenue
    FROM order_items
    GROUP BY order_id
) AS OrderRev ON r.order_id = OrderRev.order_id
GROUP BY r.review_score
ORDER BY r.review_score DESC;

-- Q22: What is the relationship between late deliveries and review scores?
-- A basic check: Average review score for orders delivered BEFORE vs AFTER estimated date
SELECT 
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late Delivery'
        ELSE 'On-Time/Early Delivery'
    END AS delivery_status,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    COUNT(r.review_id) AS total_reviews
FROM orders o
JOIN reviews r ON o.order_id = r.order_id
WHERE o.order_delivered_customer_date IS NOT NULL 
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY delivery_status;

-- Q23: Who are the top 10 sellers by total revenue?
SELECT s.seller_id, 
       s.seller_city,
       s.seller_state,
       ROUND(SUM(oi.price), 2) AS total_seller_revenue
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY total_seller_revenue DESC
LIMIT 10;

-- Q24: What is the average freight cost as a percentage of the total order value?
WITH OrderTotals AS (
    SELECT order_id, 
           SUM(price) AS product_revenue, 
           SUM(freight_value) AS freight_cost
    FROM order_items
    GROUP BY order_id
)
SELECT 
    ROUND(AVG(freight_cost / (product_revenue + freight_cost)) * 100, 2) AS avg_freight_percentage
FROM OrderTotals
WHERE product_revenue > 0;

-- Q25: What are the usage patterns for payment installments?
SELECT payment_installments, 
       COUNT(*) AS number_of_payments,
       ROUND(SUM(payment_value), 2) AS total_value
FROM payments
GROUP BY payment_installments
ORDER BY payment_installments;

-- Q26: What is the average review score by product category?
SELECT p.product_category_name, 
       ROUND(AVG(r.review_score), 2) AS avg_review_score,
       COUNT(r.review_id) AS total_reviews
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN reviews r ON oi.order_id = r.order_id
GROUP BY p.product_category_name
HAVING total_reviews > 50
ORDER BY avg_review_score DESC
LIMIT 20;

-- Q27: Which states have the highest average freight value?
SELECT c.customer_state, 
       ROUND(AVG(oi.freight_value), 2) AS avg_freight
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY avg_freight DESC;

-- Q28: How does product weight correlate with average freight value?
-- We bucket weight into ranges to see the trend
SELECT 
    CASE 
        WHEN p.product_weight_g < 1000 THEN 'Under 1kg'
        WHEN p.product_weight_g >= 1000 AND p.product_weight_g < 5000 THEN '1kg - 5kg'
        WHEN p.product_weight_g >= 5000 AND p.product_weight_g < 15000 THEN '5kg - 15kg'
        ELSE 'Over 15kg'
    END AS weight_bucket,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
WHERE p.product_weight_g IS NOT NULL
GROUP BY weight_bucket
ORDER BY avg_freight ASC;

-- Q29: What is the cancellation rate by product category?
SELECT p.product_category_name,
       COUNT(CASE WHEN o.order_status = 'canceled' THEN 1 END) AS canceled_orders,
       COUNT(o.order_id) AS total_orders,
       ROUND(CAST(COUNT(CASE WHEN o.order_status = 'canceled' THEN 1 END) AS FLOAT) / COUNT(o.order_id) * 100, 2) AS cancellation_rate
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.product_category_name
HAVING total_orders > 100
ORDER BY cancellation_rate DESC
LIMIT 15;

-- Q30: What is the distribution of orders by hour of the day?
SELECT SUBSTR(order_purchase_timestamp, 12, 2) AS hour_of_day, 
       COUNT(order_id) AS total_orders
FROM orders
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY hour_of_day
ORDER BY hour_of_day;
