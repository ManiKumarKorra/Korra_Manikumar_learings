from airflow.models import DAG, TaskInstance
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import PythonOperator
from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.exceptions import AirflowSkipException

# from datetime import datetime, timedelta
# from airflow.utils.dates import datetime

from datetime import datetime, timedelta

# import datetime
 
import csv
import logging
import pandas as pd
 
from store_info_service.shoppertrak_tasks import move_data_to_s3

 
 
DAG_ID="shoppertrak_footfall1"
SFTP_CONN_ID = "sftp_conn"
AWS_CONN_ID = "aws_conn"
# SFTP_PATH = "uploads/mani"


 
SFTP_FILE_PATTERN = "uploads/mani/KurtGeigerDailyReport_%s.csv"
S3_BUCKET = "korramanikumar"
S3_BUCKET_PATH = "Data/"
S3_FILE_PATTERN = "KurtGeigerDailyReport_%s.csv"
 
SNOWFLAKE_CONN_ID = "snowflake_conn"
SNOWFLAKE_DATABASE = "airflow_db"
SNOWFLAKE_SCHEMA = "public"
SNOWFLAKE_TABLE= "footfall"
SNOWFLAKE_STAGE="manhattan/"
SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
 
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    "params": {
        "file_name": S3_FILE_PATTERN,
        "bucket_path": S3_BUCKET_PATH,
        "bucket_name": S3_BUCKET
    },
    'catchup': True
}
 
import logging

import logging
import json

# def process_remote_sftp_csv_file(task_instance, **kwargs):
#     sftp_hook = SFTPHook(ssh_conn_id=SFTP_CONN_ID)

#     remote_file_path = f"{SFTP_FILE_PATTERN % task_instance.execution_date.strftime('%Y-%m-%d')}"

#     with sftp_hook.get_conn() as sftp_client:
#         with sftp_client.open(remote_file_path, 'r') as remote_file:
#             csv_content = remote_file.read().decode('utf-8')
#     execution_date = task_instance.execution_date.strftime("%d/%m/%Y")

#     processed_csv_content = []
#     for line in csv_content.split('\n'):
#         if not line.strip():  # Skip empty lines
#             continue
#         processed_line = f"{line.strip()},{execution_date}"
#         processed_csv_content.append(processed_line)

#     processed_csv_content_str = '\n'.join(processed_csv_content)
#     task_instance.xcom_push(key='processed_csv_content', value=processed_csv_content_str)


def process_remote_sftp_csv_file(task_instance: TaskInstance, **kwargs):
    sftp_hook = SFTPHook(ssh_conn_id=SFTP_CONN_ID)
    file_from_pattern = SFTP_FILE_PATTERN % task_instance.execution_date.strftime('%Y-%m-%d')
    # file_from_pattern = sftp_hook.get_file_by_pattern(path=SFTP_PATH, fnmatch_pattern=SFTP_FILE_PATTERN % task_instance.execution_date.strftime('%Y-%m-%d'))

    logging.info(f"Fetching file from SFTP: {file_from_pattern}")
    
    if file_from_pattern:
        with sftp_hook.get_conn() as sftp_client:
            with sftp_client.open(file_from_pattern , 'r') as remote_file:
                csv_data = remote_file.read().decode('utf-8')
        execution_date = task_instance.execution_date.strftime("%d/%m/%Y")
        transformed_data = []
        for line in csv_data.split('\n'):
            if not line.strip():  
                continue
            processed_line = f"{line.strip()},{execution_date}"
            transformed_data.append(processed_line)
            shoppertrak_transformed_data = '\n'.join(transformed_data)
            task_instance.xcom_push(key='processed_csv_content', value=shoppertrak_transformed_data)  
    else:
        raise AirflowSkipException
    sftp_hook.close_conn()

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description='A DAG to retrieve CSV files from remote SFTP server',
    schedule_interval='@daily',
    start_date=datetime(2024, 5, 15)
) as dag:

    find_remote_csv_task = PythonOperator(
        task_id='find_remote_csv_file',
        python_callable=process_remote_sftp_csv_file,
        provide_context=True
    )

# process_csv_task = PythonOperator(
#     task_id='process_csv_content',
#     python_callable=process_csv_content,
#     provide_context=True,
#     dag=dag
# )
move_shoppertrak_info_data_to_s3_task = PythonOperator(
    task_id="move_shoppertrak_info_data_to_s3_task",
    python_callable=move_data_to_s3,
    provide_context=True,
    op_kwargs={},
)



copy_s3_snowflake_to_foot_fall_daily_table = SnowflakeOperator(
        task_id="copy_s3_snowflake_to_foot_fall_daily_table",
        snowflake_conn_id=SNOWFLAKE_CONN_ID,
        sql="copy_s3_snowflake_to_foot_fall_daily.sql",
        params={
            "database": SNOWFLAKE_DATABASE,
            "schema": SNOWFLAKE_SCHEMA,
            "table": SNOWFLAKE_TABLE,
            "stage": SNOWFLAKE_STAGE,
                },
        warehouse=SNOWFLAKE_WAREHOUSE,
        dag=dag
    )

find_remote_csv_task  >> move_shoppertrak_info_data_to_s3_task >> copy_s3_snowflake_to_foot_fall_daily_table


