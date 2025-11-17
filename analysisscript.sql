-- Analytics Queries for Pizzeria Database

-- Total sales revenue per store
SELECT 
    s.store_id,
    s.address,
    s.city,
    SUM(o.total_amount) AS total_revenue
FROM Orders o
JOIN Stores s ON o.store_id = s.store_id
GROUP BY s.store_id, s.address, s.city
ORDER BY total_revenue DESC;

-- Top 10 most valuable customers by total spending
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    SUM(o.total_amount) AS total_spent
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC
LIMIT 10;

-- Most popular menu item (by quantity sold)
SELECT 
    mi.item_id,
    mi.name,
    mi.category,
    SUM(oi.quantity) AS total_quantity_sold
FROM Order_Items oi
JOIN Menu_Items mi ON oi.item_id = mi.item_id
GROUP BY mi.item_id, mi.name, mi.category
ORDER BY total_quantity_sold DESC
LIMIT 1;

-- Average order value
SELECT 
    AVG(total_amount) AS average_order_value
FROM Orders;

-- Busiest hours of the day for orders
SELECT 
    EXTRACT(HOUR FROM order_timestamp) AS hour_of_day,
    COUNT(*) AS total_orders
FROM Orders
GROUP BY hour_of_day
ORDER BY total_orders DESC;
