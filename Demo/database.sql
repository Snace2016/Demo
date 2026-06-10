
CREATE TABLE shop_appuser (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role VARCHAR(20) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    login VARCHAR(254) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);


CREATE TABLE shop_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE shop_manufacturer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE shop_supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE shop_product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(300) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES shop_category(id),
    manufacturer_id INTEGER NOT NULL REFERENCES shop_manufacturer(id),
    supplier_id INTEGER NOT NULL REFERENCES shop_supplier(id),
    discount DECIMAL(5, 2) NOT NULL DEFAULT 0,
    quantity INTEGER UNSIGNED NOT NULL DEFAULT 0,
    description TEXT NOT NULL,
    image VARCHAR(255) NOT NULL
);


CREATE TABLE shop_pickuppoint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address VARCHAR(300) NOT NULL
);


CREATE TABLE shop_orderstatus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE shop_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER UNSIGNED NOT NULL UNIQUE,
    status_id INTEGER NOT NULL REFERENCES shop_orderstatus(id),
    pickup_point_id INTEGER NOT NULL REFERENCES shop_pickuppoint(id),
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    client_id INTEGER NOT NULL REFERENCES shop_appuser(id),
    pickup_code INTEGER UNSIGNED NOT NULL
);


CREATE TABLE shop_orderitem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES shop_order(id),
    product_id INTEGER NOT NULL REFERENCES shop_product(id),
    quantity INTEGER UNSIGNED NOT NULL
);
