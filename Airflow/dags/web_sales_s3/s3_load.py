import csv
import logging
import os
from datetime import datetime
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import DAG, TaskInstance
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.dates import days_ago
from web_sales_s3.tasks import move_data_to_s3

DAG_ID = "web_sales_load"
AWS_CONN_ID = "aws_conn"
SOURCE_S3_BUCKET = "korramanikumar"
SOURCE_S3_FILE_NAME = "Data/Data-%s.csv" % datetime.now().strftime("%Y-%m-%d")
DEST_S3_BUCKET = "korramanikumar"
DEST_S3_BUCKET_PATH = "transformated_data/"
DEST_S3_FILE_PATTERN = "data-%s.csv" % datetime.now().strftime("%Y-%m-%d")

SNOWFLAKE_CONN_ID = "snowflake_conn"
SNOWFLAKE_DATABASE = "airflow_db"
SNOWFLAKE_SCHEMA = "public"
SNOWFLAKE_TABLE = "new_table"
SNOWFLAKE_STAGE = "web_sales/"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'catchup': False,
    "params": {
        "dest_file_name": DEST_S3_FILE_PATTERN,
        "dest_bucket_path": DEST_S3_BUCKET_PATH,
        "dest_bucket_name": DEST_S3_BUCKET
    }
}

def download_from_s3(task_instance: TaskInstance, **kwargs):
    execution_date = kwargs['execution_date'].strftime("%Y-%m-%d")
    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)
    try:
        file_content = s3_hook.read_key(key=SOURCE_S3_FILE_NAME, bucket_name=SOURCE_S3_BUCKET)
        logging.info(f"Response object is: {file_content}")
        
        if not file_content:
            logging.info("No file found matching the pattern.")
            return

        csv_content = file_content.splitlines()
   

        csv_reader = csv.reader(csv_content)
        rows = list(csv_reader)

        if rows:
            header = rows[0]
            header.append('file_upload_date')
            for row in rows[1:]:
                row.append(execution_date)

        modified_content = '\n'.join([','.join(row) for row in rows])
        task_instance.xcom_push(key='downloaded_file', value=modified_content)
    except Exception as ex:
        raise RuntimeError(f"Error reading file from S3: {ex}")

with DAG(
    DAG_ID,
    description="Copy data from S3 bucket and load into Snowflake 'web_sales' table",
    default_args=default_args,
    start_date=datetime(2024, 5, 10),
    schedule_interval='@daily',
    catchup=False
) as dag:

    download_from_s3_task = PythonOperator(
        task_id="download_from_s3_task",
        python_callable=download_from_s3,
        provide_context=True,
    )

    move_data_to_s3_task = PythonOperator(
        task_id="move_data_to_s3_task",
        python_callable=move_data_to_s3,
        provide_context=True,
        op_kwargs={},
    )

    copy_s3_snowflake_to_web_sales_table = SnowflakeOperator(
        task_id="copy_s3_snowflake_to_web_sales_table",
        snowflake_conn_id=SNOWFLAKE_CONN_ID,
        sql="copy_s3_snowflake_to_new_table.sql",
        params={
            "database": SNOWFLAKE_DATABASE,
            "schema": SNOWFLAKE_SCHEMA,
            "table": SNOWFLAKE_TABLE,
            "stage": SNOWFLAKE_STAGE,
        },
        warehouse=SNOWFLAKE_WAREHOUSE,
        dag=dag
    )

    download_from_s3_task >> move_data_to_s3_task >> copy_s3_snowflake_to_web_sales_table
