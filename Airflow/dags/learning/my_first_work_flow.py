from datetime import datetime
from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 4, 24),
    'retries': 1
}

with DAG('my_first_workflow', default_args=default_args, schedule_interval=None) as dag:

    # Task 1: Create Snowflake table
    create_table_task = SnowflakeOperator(
        task_id="create_table",
        sql='''
        CREATE OR REPLACE TABLE s3data (
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
        )
        ''',
        snowflake_conn_id="snowflake_conn"
    )

    # Task 2: Create External Stage
    create_stage_task = SnowflakeOperator(
    task_id="create_stage",
    sql='''
            create stage airflowstage
    storage_integration = s3_int
    url = 's3://korramanikumar/Data/'
    ''',
    snowflake_conn_id="snowflake_conn"
)



    # Task 3: Load data from AWS S3 to Snowflake
    copy_data_task = SnowflakeOperator(
        task_id='copy_data',
        sql='''
        COPY INTO s3data
        FROM @airflowstage
        PATTERN='.*Sample100csv.csv'
        FILE_FORMAT = (FORMAT_NAME = my_csv_format)
        ON_ERROR = CONTINUE;  -- Adjust error handling as needed
        ''',
        snowflake_conn_id='snowflake_conn'
    )

    # Define task dependencies
    create_table_task >> create_stage_task >> copy_data_task


    
