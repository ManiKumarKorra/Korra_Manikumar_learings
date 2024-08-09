USE SCHEMA AIRFLOW_DB.PUBLIC;

CREATE OR REPLACE TABLE SCHEMACHANGE_DEMO
(
    id INT,
            product_name VARCHAR,
            customer_name VARCHAR,
            order_id INT,
            sales DECIMAL(18, 2),
            quantity INT,
            discount DECIMAL(18, 2),
            region VARCHAR,
            category VARCHAR,
            profit DECIMAL(18, 2)
);