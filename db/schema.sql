-- Dimensions
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id          VARCHAR PRIMARY KEY,
    customer_unique_id   VARCHAR,
    customer_zip_code    VARCHAR,
    customer_city        VARCHAR,
    customer_state       VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_seller (
    seller_id        VARCHAR PRIMARY KEY,
    seller_zip_code  VARCHAR,
    seller_city      VARCHAR,
    seller_state     VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id                    VARCHAR PRIMARY KEY,
    product_category_name         VARCHAR,
    product_weight_g              NUMERIC,
    product_length_cm             NUMERIC,
    product_height_cm             NUMERIC,
    product_width_cm              NUMERIC
);

CREATE TABLE IF NOT EXISTS dim_geolocation (
    geo_id        SERIAL PRIMARY KEY,
    zip_code      VARCHAR,
    city          VARCHAR,
    state         VARCHAR
);

-- Facts
CREATE TABLE IF NOT EXISTS fact_order (
    order_id            VARCHAR PRIMARY KEY,
    customer_id         VARCHAR REFERENCES dim_customer(customer_id),
    order_status        VARCHAR,
    order_purchase_ts   TIMESTAMP,
    order_approved_ts   TIMESTAMP,
    order_delivered_ts  TIMESTAMP,
    order_estimated_ts  TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_order_item (
    order_id          VARCHAR REFERENCES fact_order(order_id),
    order_item_id     INTEGER,
    product_id        VARCHAR REFERENCES dim_product(product_id),
    seller_id         VARCHAR REFERENCES dim_seller(seller_id),
    shipping_limit_ts TIMESTAMP,
    price             NUMERIC,
    freight_value     NUMERIC,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE IF NOT EXISTS fact_payment (
    order_id          VARCHAR REFERENCES fact_order(order_id),
    payment_sequential INTEGER,
    payment_type       VARCHAR,
    payment_installments INTEGER,
    payment_value      NUMERIC,
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE IF NOT EXISTS fact_review (
    review_id                VARCHAR PRIMARY KEY,
    order_id                 VARCHAR REFERENCES fact_order(order_id),
    review_score             INTEGER,
    review_creation_ts       TIMESTAMP,
    review_answer_ts         TIMESTAMP
);
