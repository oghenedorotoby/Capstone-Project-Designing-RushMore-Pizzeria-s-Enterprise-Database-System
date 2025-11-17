---creating STORES
CREATE TABLE Stores (
    store_id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---creating CUSTOMERS
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---creating INGREDIENTS
CREATE TABLE Ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    stock_quantity NUMERIC(10, 2) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL
);

--- creating MENU ITEMS
CREATE TABLE Menu_Items (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    size VARCHAR(20)
);

--- creating ORDERS
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES Customers(customer_id) ON DELETE SET NULL,
    store_id INTEGER REFERENCES Stores(store_id) ON DELETE RESTRICT,
    order_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10, 2) NOT NULL
);

--- creating ORDER ITEMS (Junction Table between Orders and Menu_Items)
CREATE TABLE Order_Items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES Orders(order_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES Menu_Items(item_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_per_item NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) GENERATED ALWAYS AS (quantity * price_per_item) STORED
);

--- creating MENU ITEM INGREDIENTS (Junction Table between Menu_Items and Ingredients)
CREATE TABLE Menu_Item_Ingredients (
    menu_item_ingredient_id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES Menu_Items(item_id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES Ingredients(ingredient_id) ON DELETE RESTRICT,
    quantity_required NUMERIC(10, 2) NOT NULL CHECK (quantity_required > 0)
);

CREATE INDEX idx_orders_customer_id ON Orders(customer_id);
CREATE INDEX idx_orders_store_id ON Orders(store_id);
CREATE INDEX idx_order_items_order_id ON Order_Items(order_id);
CREATE INDEX idx_menu_item_ingredients_item_id ON Menu_Item_Ingredients(item_id);