
from airflow.models import DAG, TaskInstance

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import datetime
import os
import logging
import csv 


 
# Define the S3 bucket and file details
SOURCE_S3_BUCKET = "korramanikumar"
 
# '.*DOM-%s.*[.]csv' % datetime.now().strftime("%Y-%m-%d")
SOURCE_S3_FILE_NAME = "Data/Data-%s.csv" % datetime.now().strftime("%Y-%m-%d")  
 
# # Define the directory to download the file to
# DOWNLOAD_DIR = "/tmp"
 
# Function to download the file from S3
def download_from_s3(task_instance: TaskInstance, **kwargs):
    execution_date = kwargs['execution_date'].strftime("%Y-%m-%d")
    s3_hook = S3Hook(aws_conn_id="aws_conn")  # Assuming you have set up the AWS connection in Airflow
    try:
        file_content = s3_hook.read_key(key=SOURCE_S3_FILE_NAME, bucket_name=SOURCE_S3_BUCKET)
        logging.info(f"Response object is: {file_content}")
        if file_content:
            csv_content = file_content.split('\n')
            if csv_content:
                # Modify header to include 'file_upload_date'
                header = csv_content[0].strip().split(',')
                header.append('file_upload_date')
                modified_content = [','.join(header)]
                # Modify data rows to include 'execution_date'
                for row in csv_content[1:]:
                    row_data = row.strip().split(',')
                    row_data.append(execution_date)
                    modified_content.append(','.join(row_data))
                modified_content = '\n'.join(modified_content)
                logging.info()
                task_instance.xcom_push(key='downloaded_file', value=modified_content)
            else:
                logging.info("No CSV data found in S3.")
        else:
            logging.info("No file found matching the pattern.")
    except Exception as ex:
        raise RuntimeError(f"Error reading file from S3: {ex}")


# Define the DAG
with DAG(
    "download_from_s3_dag",
    start_date=datetime(2024, 5, 7),
    schedule_interval=None,  # You can set the schedule interval as needed
    catchup=False,
) as dag:
    # Define the task to download the file from S3
    download_from_s3_task = PythonOperator(
        task_id="download_from_s3_task",
        python_callable=download_from_s3
    )

download_from_s3_task