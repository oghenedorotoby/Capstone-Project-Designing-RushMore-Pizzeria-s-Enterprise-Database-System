#!/usr/bin/env python3

import os
import random
import decimal
import yaml
from faker import Faker
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

def truncate(value, length):
    return value[:length] if value else value

def load_config():
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    else:
        raise FileNotFoundError("config.yaml not found")

config = load_config()
db_conf = config["database"]

conn = psycopg2.connect(
    host=db_conf["host"],
    dbname=db_conf["dbname"],
    user=db_conf["user"],
    password=db_conf["password"]
)

cursor = conn.cursor()
print("Connected successfully!")

def get_db_config():
    # 1. Load from config.yaml if present
    if os.path.exists("config.yaml"):
        print("Loading DB config from config.yaml...")
        with open("config.yaml", "r") as f:
            cfg = yaml.safe_load(f)
            return cfg["database"]


# Basic validation
db_cfg = get_db_config()
missing = [k for k,v in db_cfg.items() if v is None]
if missing:
    raise SystemExit(f"Missing DB config parameters: {missing}. Set environment variables or provide config.yaml/.env.")

# Globals for sizes and categories
CATEGORIES = ["Pizza", "Drink", "Side"]
PIZZA_SIZES = ["Small", "Medium", "Large", "Extra Large"]
DRINK_SIZES = ["330ml", "500ml", "750ml"]
SIDE_SIZES = ["Single", "Share"]
FAKE = Faker()
random.seed(42)
Faker.seed(42)

# Target volumes
NUM_STORES = random.randint(3, 5)
NUM_MENU_ITEMS = random.randint(20, 30)
NUM_INGREDIENTS = random.randint(40, 50)
NUM_CUSTOMERS = 1200  # >1000
NUM_ORDERS = 5500     # >5000
AVG_ITEMS_PER_ORDER = 3

# Utility helpers
def decimal_round(v, places=2):
    return decimal.Decimal(v).quantize(decimal.Decimal(10) ** -places)

def connect():
    return psycopg2.connect(
        host=db_cfg["host"],
        port=db_cfg.get("port", 5432),
        dbname=db_cfg["dbname"],
        user=db_cfg["user"],
        password=db_cfg["password"]
    )

def bulk_insert(cursor, table, columns, values, returning=False):
    """
    Helper wrapper around psycopg2.extras.execute_values.
    If returning=True, fetches and returns generated ids (works if DB supports RETURNING).
    """
    cols = ", ".join(columns)
    tmpl = "(" + ",".join(["%s"] * len(columns)) + ")"
    sql = f"INSERT INTO {table} ({cols}) VALUES %s"
    if returning:
        sql += " RETURNING *"
        execute_values(cursor, sql, values, template=tmpl)
        return cursor.fetchall()
    else:
        execute_values(cursor, sql, values, template=tmpl)


def main():
    print("Connecting to DB:", db_cfg["host"], db_cfg["dbname"])
    conn = connect()
    conn.autocommit = False
    cur = conn.cursor()
    try:
        # 1) Create Stores
        print(f"Creating {NUM_STORES} stores...")
        store_rows = []
        for i in range(NUM_STORES):
            address = FAKE.address().replace("\n", ", ")
            city = FAKE.city()
            phone = truncate(FAKE.phone_number(), 20) 
            store_rows.append((address, city, phone))
        # Insert and get generated ids
        execute_values(cur,
                       "INSERT INTO Stores (address, city, phone_number) VALUES %s RETURNING store_id",
                       store_rows)
        store_ids = [r[0] for r in cur.fetchall()]
        print("Store IDs:", store_ids)

        # 2) Create Ingredients
        print(f"Creating {NUM_INGREDIENTS} ingredients...")
        ingredient_names_pool = [
            "Mozzarella Cheese", "Cheddar Cheese", "Parmesan", "Pepperoni", "Italian Sausage",
            "Bacon", "Ham", "Chicken", "Beef", "Onion", "Green Pepper", "Red Pepper",
            "Mushroom", "Black Olives", "Green Olives", "Tomato Sauce", "Pesto", "BBQ Sauce",
            "Garlic", "Spinach", "Basil", "Oregano", "Chili Flakes", "Pineapple", "Jalapeno",
            "Anchovies", "Ricotta", "Feta", "Corn", "Potato", "Rosemary", "Thyme", "Butter",
            "Sugar", "Salt", "Yeast", "Pizza Dough", "Tomato", "Lettuce", "Cucumber", "Carrot",
            "Ranch Dressing", "Blue Cheese", "Sliced Tomatoes", "Olive Oil", "Lemon Juice",
            "Vinegar", "Ketchup", "Mustard", "Pickles", "BBQ Rub"
        ]
        random.shuffle(ingredient_names_pool)
        ingredient_names = ingredient_names_pool[:NUM_INGREDIENTS]
        ingredient_rows = []
        for name in ingredient_names:
            stock = float(round(random.uniform(5.0, 200.0), 2))
            unit = truncate(random.choice(["kg", "units", "liters", "g"]), 20)
            ingredient_rows.append((name, stock, unit))
        execute_values(cur,
                       "INSERT INTO Ingredients (name, stock_quantity, unit) VALUES %s RETURNING ingredient_id",
                       ingredient_rows)
        ingredient_ids = [r[0] for r in cur.fetchall()]
        print("Inserted ingredients:", len(ingredient_ids))

        # 3) Create Menu Items
        print(f"Creating {NUM_MENU_ITEMS} menu items...")
        menu_rows = []
        sample_pizza_names = ["Margherita", "Pepperoni", "Hawaiian", "Veggie", "Meat Lovers", "BBQ Chicken",
                              "Four Cheese", "Pesto Chicken", "Mediterranean", "Buffalo"]
        sample_side_names = ["Garlic Bread", "Chicken Wings", "Salad", "Fries", "Mozzarella Sticks"]
        sample_drink_names = ["Coke", "Diet Coke", "Sprite", "Bottled Water", "Orange Juice", "Iced Tea"]
        for i in range(NUM_MENU_ITEMS):
            category = random.choice(CATEGORIES)
            if category == "Pizza":
                base = random.choice(sample_pizza_names)
                size = truncate(random.choice(PIZZA_SIZES), 20)
                name = f"{size} {base} Pizza"
                price = round(random.uniform(8, 25) + (PIZZA_SIZES.index(size) * 3), 2)
            elif category == "Side":
                base = random.choice(sample_side_names)
                size = truncate(random.choice(SIDE_SIZES), 20)
                name = f"{base} ({size})"
                price = round(random.uniform(3, 12), 2)
            else:  # Drink
                base = random.choice(sample_drink_names)
                size = truncate(random.choice(DRINK_SIZES), 20)
                name = f"{base} {size}"
                price = round(random.uniform(1.5, 5.5), 2)
            menu_rows.append((name, category, size, decimal_round(price)))
        # Insert and collect item ids
        execute_values(cur,
                       "INSERT INTO Menu_Items (name, category, size) VALUES %s RETURNING item_id, name",
                       [(r[0], r[1], r[2]) for r in menu_rows])
        menu_return = cur.fetchall()
        item_ids = [r[0] for r in menu_return]
        item_names = [r[1] for r in menu_return]
        # store prices in a dict for later use when generating order_items
        # We'll create a minimal price map (item_id->price) using the menu_rows order
        price_map = {}
        for (item_id, _name), (_name2, cat, size, price) in zip(menu_return, menu_rows):
            price_map[item_id] = decimal_round(price)

        print("Inserted menu items:", len(item_ids))

        # 4) Map Menu Items to Ingredients (Menu_Item_Ingredients)
        print("Creating Menu_Item_Ingredients mappings...")
        mii_rows = []
        for item_id in item_ids:
            # Each menu item uses 2-8 ingredients depending on category
            # pizzas: more ingredients, drinks: 1-2, sides: 2-5
            # find category quickly
            # We'll randomize ingredient selection
            category = random.choice(CATEGORIES)  # intentionally random to vary mapping
            if "Pizza" in category:
                num_ing = random.randint(3, 8)
            elif "Side" in category:
                num_ing = random.randint(2, 5)
            else:
                num_ing = random.randint(1, 2)
            chosen = random.sample(ingredient_ids, min(num_ing, len(ingredient_ids)))
            for ing_id in chosen:
                qty = decimal_round(random.uniform(0.05, 2.0))  # reasonable amounts
                mii_rows.append((item_id, ing_id, qty))
        if mii_rows:
            execute_values(cur,
                           "INSERT INTO Menu_Item_Ingredients (item_id, ingredient_id, quantity_required) VALUES %s",
                           mii_rows)
        print(f"Inserted {len(mii_rows)} menu_item_ingredient rows")

        # 5) Create Customers
        print(f"Creating {NUM_CUSTOMERS} customers...")
        customer_rows = []
        emails = set()
        phones = set()
        for i in range(NUM_CUSTOMERS):
            first = FAKE.first_name()
            last = FAKE.last_name()
            # ensure unique-ish emails and phones (Faker sometimes duplicates)
            email = None
            attempt = 0
            while True:
                attempt += 1
                email = FAKE.email()
                if email not in emails or attempt > 5:
                    emails.add(email)
                    break
            phone = None
            attempt = 0
            while True:
                attempt += 1
                phone = truncate(FAKE.phone_number(), 20)
                if phone not in phones or attempt > 5:
                    phones.add(phone)
                    break
            customer_rows.append((first, last, email, phone))
            if (i+1) % 200 == 0:
                print(f"  Prepared {i+1} customers...")
        # Bulk insert customers and capture IDs
        execute_values(cur,
                       "INSERT INTO Customers (first_name, last_name, email, phone_number) VALUES %s RETURNING customer_id",
                       customer_rows)
        customer_ids = [r[0] for r in cur.fetchall()]
        print("Inserted customers:", len(customer_ids))

        # 6) Create Orders
        print(f"Creating {NUM_ORDERS} orders (and their order_items)...")
        # We'll generate orders in batches to avoid huge memory usage
        ORDERS_BATCH = 500
        order_id_list = []
        order_items_insert_rows = []
        order_rows_batch = []
        generated_orders = 0
        generated_order_items = 0

        # Prepare a mapping for quick random picks
        store_ids_cycle = store_ids.copy()
        # create a list of item ids for sampling when generating order_items
        item_ids_list = item_ids.copy()

        for batch_start in range(0, NUM_ORDERS, ORDERS_BATCH):
            batch_end = min(batch_start + ORDERS_BATCH, NUM_ORDERS)
            order_rows_batch = []
            # create order rows for this batch (without total_amount for now)
            for _ in range(batch_start, batch_end):
                cust_id = random.choice(customer_ids)
                store_id = random.choice(store_ids_cycle)
                order_ts = FAKE.date_time_this_year()  # returns datetime within this year
                # total_amount placeholder; we'll compute from order_items later
                order_rows_batch.append((cust_id, store_id, order_ts, decimal_round(0)))
            # Insert orders and get generated order_ids in same order
            execute_values(cur,
                           "INSERT INTO Orders (customer_id, store_id, order_timestamp, total_amount) VALUES %s RETURNING order_id",
                           order_rows_batch)
            inserted_orders = [r[0] for r in cur.fetchall()]
            # For each order, generate between 1 and 6 items (avg ~3)
            for order_id in inserted_orders:
                num_items = max(1, int(random.gauss(AVG_ITEMS_PER_ORDER, 1)))  # gaussian for variation
                chosen_items = random.choices(item_ids_list, k=num_items)
                order_total = decimal.Decimal("0.00")
                for itm in chosen_items:
                    qty = random.randint(1, 3)
                    price = price_map.get(itm, decimal_round(random.uniform(3, 15)))
                    subtotal = decimal_round(price * qty)
                    order_items_insert_rows.append((order_id, itm, qty, price))
                    order_total += subtotal
                    generated_order_items += 1
                # Update order total in DB (do a parameterized update per order to keep it simple)
                cur.execute("UPDATE Orders SET total_amount = %s WHERE order_id = %s",
                            (decimal_round(order_total), order_id))
            generated_orders += len(inserted_orders)
            print(f"  Inserted orders: {generated_orders}; accumulated order_items rows: {len(order_items_insert_rows)}")

            # Periodically flush order_items in bulk to DB to avoid memory blowup
            if len(order_items_insert_rows) >= 2000:
                execute_values(cur,
                               "INSERT INTO Order_Items (order_id, item_id, quantity, price_per_item) VALUES %s",
                               order_items_insert_rows)
                order_items_insert_rows = []
                conn.commit()
                print("  Flushed 2000+ order_items to DB and committed")

        # flush any remaining order_items
        if order_items_insert_rows:
            execute_values(cur,
                           "INSERT INTO Order_Items (order_id, item_id, quantity, price_per_item) VALUES %s",
                           order_items_insert_rows)
            print(f"Flushed final {len(order_items_insert_rows)} order_items")

        conn.commit()
        print(f"Done. Inserted approx {NUM_ORDERS} orders and ~{generated_order_items} order_items (approx).")
    except Exception as e:
        conn.rollback()
        print("ERROR occurred; rolled back. Exception:", e)
        raise
    finally:
        cur.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
