from airflow.models import DAG, TaskInstance
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import PythonOperator
from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from fnmatch import fnmatch

# from datetime import datetime, timedelta
# from airflow.utils.dates import datetime

from datetime import datetime, timedelta

# import datetime
 
import csv
import logging
 
from store_info_service.shoppertrak_tasks import move_data_to_s3
 
 
DAG_ID="shoppertrak_foot_fall_daily_load"
SFTP_CONN_ID = "live_shoppertrak_sftp"
AWS_CONN_ID = "aws_conn"
 
SFTP_PATH = "Foot/"
SFTP_FILE_PATTERN = "KurtGeigerDailyReport_%s.csv"
S3_BUCKET = "korramanikumar"
S3_BUCKET_PATH = "Data/"
S3_FILE_PATTERN = "KurtGeigerDailyReport_%s.csv"
 
SNOWFLAKE_CONN_ID = "snowflake_conn"
SNOWFLAKE_DATABASE = "airflow_db"
SNOWFLAKE_SCHEMA = "public"
SNOWFLAKE_TABLE= "foot_fall_daily"
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
 
def find_remote_sftp_csv_file(task_instance: TaskInstance, **kwargs):
    sftp_hook = SFTPHook(ssh_conn_id=SFTP_CONN_ID)
 
 
    file_from_pattern = sftp_hook.get_file_by_pattern(path=SFTP_PATH, fnmatch_pattern=SFTP_FILE_PATTERN % task_instance.execution_date.strftime('%Y-%m-%d'))
    if file_from_pattern:
        logging.info("Found file from SFTP: %s", file_from_pattern)
        task_instance.xcom_push(key="shoppertrak_sftp_remote_filename", value=file_from_pattern)
    else:
        raise AirflowSkipException
    

 
 
    sftp_hook.close_conn()
 
def file_upload_date(task_instance: TaskInstance, **kwargs):
        execution_date = task_instance.execution_date.strftime("%d%m%Y")
        download_csv_data = task_instance.xcom_pull(key='shoppertrak_sftp_remote_filename')
        logging.info("Downloaded CSV data: %s", download_csv_data)
        shoppertrak_data = csv.reader(download_csv_data.splitlines())
        csv_data = []
        for row in shoppertrak_data:
            row.append(execution_date)
            csv_data.append(row)
        logging.info("CSV data: %s", csv_data)
        task_instance.xcom_push(key="shoppertrak_report_data", value=csv_data)

 
 
with DAG(
    DAG_ID,
    description="Copy data from sftp to S3 bucket and load into snowflake 'foot_fall_daily' table",
    default_args=default_args,
    start_date=datetime(2023, 12, 2, 0, 0, 0),
    schedule_interval='@daily',
    # template_searchpath="dags/includes/sql/shoppertrak/",
    max_active_runs=1,
    tags=["sftp", "s3", "shoppertrak", "foot_fall_daily", "snowflake", "live"],
    catchup=True
) as dag:
   
    find_remote_sftp_csv_file = PythonOperator(
        task_id="find_remote_sftp_csv_file",
        python_callable=find_remote_sftp_csv_file
    )
 
 
    file_upload_date_task = PythonOperator(
        task_id='file_upload_date_task',
        python_callable=file_upload_date,
        provide_context=True,
        dag=dag,
    )
 
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
 
    find_remote_sftp_csv_file >> file_upload_date_task >> move_shoppertrak_info_data_to_s3_task  >> copy_s3_snowflake_to_foot_fall_daily_table