🍕 RushMore Pizzeria – Enterprise Database System
Capstone Project – Cloud Database Design, ETL, and Analytics
This project designs and implements a full cloud-hosted PostgreSQL enterprise database for RushMore Pizzeria. It includes complete data modeling, ETL population script, data analytics queries, and a BI-ready database deployed on Azure PostgreSQL.
________________________________________
📌 Project Overview
RushMore Pizzeria is expanding its operations and requires a scalable, secure, and analytics-ready cloud database. This project delivers:
✔ A fully normalized OLTP-style relational schema
✔ Cloud-hosted Azure PostgreSQL database
✔ A Python ETL script that populates the database with fake but realistic data
✔ SQL analytics queries for key business insights
✔ Documentation, ERD, and architecture overview
________________________________________
🏗️ System Architecture
Components:
•	PostgreSQL on Azure (cloud database)
•	Python ETL using:
o	psycopg2-binary
o	Faker
o	.env/config.yaml for credentials
•	GitHub Repository for version control
 
The schema follows 3rd Normal Form (3NF) for minimal redundancy and maximum integrity.
________________________________________
🗄️ Database Schema (3NF Normalized)
Tables Included
•	Stores
•	Customers
•	Ingredients
•	Menu_Items
•	Orders
•	Order_Items (bridge table)
The schema enforces:
•	Primary keys
•	Foreign keys with ON DELETE rules
•	Unique constraints
•	Referential integrity
•	Proper indexing for analytics
________________________________________
🧪 Data Generation (populate.py)
The populate.py script automatically fills the cloud database with realistic fake data:
Volumes Generated
•	Stores: 3–5
•	Menu Items: 20–30
•	Ingredients: 40–50
•	Customers: 1,000+
•	Orders: 5,000+
•	Order Items: ~15,000+
Tech Used
•	Faker() for realistic PII
•	execute_values() for fast bulk inserts
•	Reads credentials via:
o	.env
o	or config.yaml
________________________________________
🔑 Environment Configuration
Create a config.yaml file
________________________________________
📊 Analytics Queries (Part 5)
These SQL queries answer key business questions.
1️⃣ Total Sales Revenue per Store
SELECT s.store_id, s.city, SUM(o.total_amount) AS revenue
FROM Orders o
JOIN Stores s ON o.store_id = s.store_id
GROUP BY s.store_id, s.city
ORDER BY revenue DESC;
2️⃣ Top 10 Most Valuable Customers
SELECT c.customer_id, c.first_name, c.last_name,
       SUM(o.total_amount) AS total_spent
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 10;
3️⃣ Most Popular Menu Item
SELECT mi.name, SUM(oi.quantity) AS qty_sold
FROM Order_Items oi
JOIN Menu_Items mi ON oi.item_id = mi.item_id
GROUP BY mi.name
ORDER BY qty_sold DESC
LIMIT 1;
4️⃣ Average Order Value
SELECT AVG(total_amount) AS average_order_value
FROM Orders;
5️⃣ Busiest Hours of the Day
SELECT EXTRACT(HOUR FROM order_timestamp) AS hour,
       COUNT(*) AS order_count
FROM Orders
GROUP BY hour
ORDER BY order_count DESC;
A file is included at:
📁 /sql/analytics_queries.sql
________________________________________
🚀 How to Run the ETL Script
1.	Install dependencies:
pip install -r requirements.txt
2.	Make sure  config.yaml is created.
3.	Run the script:
python populate.py
________________________________________
📦 Project Structure
Capstone-Project/
│
├── scripts/
│   └── populate.py
│
├── sql/
│   ├── create_schema.sql
│   └── analytics_queries.sql
│
├── screenshots/
│   ├── erd.png
│   └── bi_dashboard.png
│
├── README.md
└── requirements.txt
________________________________________
🧠 Key Challenges Solved
•	Schema normalization to 3NF
•	Cloud database authentication issues
•	Bulk insert performance (fixed using execute_values)
•	Truncation of long Faker fields
•	Ensuring referential integrity
•	Handling password/auth security
________________________________________
🏁 Conclusion
This project successfully delivers a production-grade, cloud-ready relational database with:
✔ Scalable OLTP architecture
✔ Realistic test data
✔ Analytics-driven SQL queries
✔ Professional documentation
✔ BI reporting capability
It demonstrates strong skills in:
•	SQL database design
•	Python ETL scripting
•	Cloud database deployment
•	Data engineering best practices
•	Analytical modeling

