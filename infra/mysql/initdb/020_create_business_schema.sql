SET NAMES utf8mb4 COLLATE utf8mb4_0900_bin;
SET time_zone = '+00:00';

CREATE TABLE IF NOT EXISTS olist_oltp.product_category_translation (
    product_category_name VARCHAR(256) NOT NULL,
    product_category_name_english VARCHAR(256) NOT NULL,
    CONSTRAINT pk_product_category_translation PRIMARY KEY (product_category_name)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.customers (
    customer_id VARCHAR(64) NOT NULL,
    customer_unique_id VARCHAR(64) NOT NULL,
    customer_zip_code_prefix VARCHAR(16) NOT NULL,
    customer_city VARCHAR(256) NOT NULL,
    customer_state VARCHAR(2) NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT ck_customers_state CHECK (
        customer_state REGEXP '^[A-Z]{2}$'
    ),
    INDEX idx_customers_unique_id (customer_unique_id),
    INDEX idx_customers_location (customer_zip_code_prefix, customer_state)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.sellers (
    seller_id VARCHAR(64) NOT NULL,
    seller_zip_code_prefix VARCHAR(16) NOT NULL,
    seller_city VARCHAR(256) NOT NULL,
    seller_state VARCHAR(2) NOT NULL,
    CONSTRAINT pk_sellers PRIMARY KEY (seller_id),
    CONSTRAINT ck_sellers_state CHECK (
        seller_state REGEXP '^[A-Z]{2}$'
    ),
    INDEX idx_sellers_location (seller_zip_code_prefix, seller_state)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.products (
    product_id VARCHAR(64) NOT NULL,
    product_category_name VARCHAR(256) NULL,
    product_name_lenght INT NULL,
    product_description_lenght INT NULL,
    product_photos_qty INT NULL,
    product_weight_g INT NULL,
    product_length_cm INT NULL,
    product_height_cm INT NULL,
    product_width_cm INT NULL,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT ck_products_name_lenght CHECK (
        product_name_lenght IS NULL OR product_name_lenght >= 0
    ),
    CONSTRAINT ck_products_description_lenght CHECK (
        product_description_lenght IS NULL OR product_description_lenght >= 0
    ),
    CONSTRAINT ck_products_photos_qty CHECK (
        product_photos_qty IS NULL OR product_photos_qty >= 0
    ),
    CONSTRAINT ck_products_weight_g CHECK (
        product_weight_g IS NULL OR product_weight_g >= 0
    ),
    CONSTRAINT ck_products_length_cm CHECK (
        product_length_cm IS NULL OR product_length_cm >= 0
    ),
    CONSTRAINT ck_products_height_cm CHECK (
        product_height_cm IS NULL OR product_height_cm >= 0
    ),
    CONSTRAINT ck_products_width_cm CHECK (
        product_width_cm IS NULL OR product_width_cm >= 0
    ),
    CONSTRAINT fk_products_category FOREIGN KEY (product_category_name)
        REFERENCES olist_oltp.product_category_translation (product_category_name),
    INDEX idx_products_category (product_category_name)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.orders (
    order_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    order_status VARCHAR(32) NOT NULL,
    order_purchase_timestamp DATETIME(6) NOT NULL,
    order_approved_at DATETIME(6) NULL,
    order_delivered_carrier_date DATETIME(6) NULL,
    order_delivered_customer_date DATETIME(6) NULL,
    order_estimated_delivery_date DATETIME(6) NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT ck_orders_status CHECK (
        order_status IN (
            'created', 'approved', 'invoiced', 'processing', 'shipped',
            'delivered', 'unavailable', 'canceled'
        )
    ),
    CONSTRAINT ck_orders_approval_after_purchase CHECK (
        order_approved_at IS NULL
        OR order_approved_at >= order_purchase_timestamp
    ),
    CONSTRAINT ck_orders_customer_after_purchase CHECK (
        order_delivered_customer_date IS NULL
        OR order_delivered_customer_date >= order_purchase_timestamp
    ),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES olist_oltp.customers (customer_id),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_status_purchase (order_status, order_purchase_timestamp)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.order_items (
    order_id VARCHAR(64) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    seller_id VARCHAR(64) NOT NULL,
    shipping_limit_date DATETIME(6) NOT NULL,
    price DECIMAL(18, 2) NOT NULL,
    freight_value DECIMAL(18, 2) NOT NULL,
    CONSTRAINT pk_order_items PRIMARY KEY (order_id, order_item_id),
    CONSTRAINT ck_order_items_sequence CHECK (order_item_id > 0),
    CONSTRAINT ck_order_items_price CHECK (price >= 0),
    CONSTRAINT ck_order_items_freight CHECK (freight_value >= 0),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
        REFERENCES olist_oltp.orders (order_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id)
        REFERENCES olist_oltp.products (product_id),
    CONSTRAINT fk_order_items_seller FOREIGN KEY (seller_id)
        REFERENCES olist_oltp.sellers (seller_id),
    INDEX idx_order_items_product (product_id),
    INDEX idx_order_items_seller (seller_id)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.order_payments (
    order_id VARCHAR(64) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(32) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value DECIMAL(18, 2) NOT NULL,
    CONSTRAINT pk_order_payments PRIMARY KEY (order_id, payment_sequential),
    CONSTRAINT ck_order_payments_sequence CHECK (payment_sequential > 0),
    CONSTRAINT ck_order_payments_type CHECK (
        payment_type IN (
            'credit_card', 'boleto', 'voucher', 'debit_card', 'not_defined'
        )
    ),
    CONSTRAINT ck_order_payments_installments CHECK (payment_installments >= 0),
    CONSTRAINT ck_order_payments_value CHECK (payment_value >= 0),
    CONSTRAINT fk_order_payments_order FOREIGN KEY (order_id)
        REFERENCES olist_oltp.orders (order_id)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.order_reviews (
    review_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    review_score INT NOT NULL,
    review_comment_title VARCHAR(1024) NULL,
    review_comment_message TEXT NULL,
    review_creation_date DATETIME(6) NOT NULL,
    review_answer_timestamp DATETIME(6) NOT NULL,
    CONSTRAINT pk_order_reviews PRIMARY KEY (review_id, order_id),
    CONSTRAINT ck_order_reviews_score CHECK (review_score BETWEEN 1 AND 5),
    CONSTRAINT ck_review_answer_after_creation CHECK (
        review_answer_timestamp >= review_creation_date
    ),
    CONSTRAINT fk_order_reviews_order FOREIGN KEY (order_id)
        REFERENCES olist_oltp.orders (order_id),
    INDEX idx_order_reviews_order (order_id)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS olist_oltp.geolocation (
    geolocation_id BIGINT NOT NULL AUTO_INCREMENT,
    geolocation_zip_code_prefix VARCHAR(16) NOT NULL,
    geolocation_lat DECIMAL(18, 14) NOT NULL,
    geolocation_lng DECIMAL(18, 14) NOT NULL,
    geolocation_city VARCHAR(256) NOT NULL,
    geolocation_state VARCHAR(2) NOT NULL,
    CONSTRAINT pk_geolocation PRIMARY KEY (geolocation_id),
    CONSTRAINT ck_geolocation_lat CHECK (
        geolocation_lat BETWEEN -90 AND 90
    ),
    CONSTRAINT ck_geolocation_lng CHECK (
        geolocation_lng BETWEEN -180 AND 180
    ),
    CONSTRAINT ck_geolocation_state CHECK (
        geolocation_state REGEXP '^[A-Z]{2}$'
    ),
    INDEX idx_geolocation_lookup (
        geolocation_zip_code_prefix,
        geolocation_state
    )
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_bin;
