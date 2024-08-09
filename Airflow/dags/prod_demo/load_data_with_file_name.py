from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import logging
import os

def log_file_data_from_s3():
    s3_hook = S3Hook(aws_conn_id="aws_conn")
    files = s3_hook.list_keys(bucket_name="korramanikumar", prefix="sample_montly_data/")

    combined_data = []
    
    for file in files:
        filename = file.split("/")[-1]
        logging.info(f"File name: {filename}")

        # Load file data from S3
        file_data = s3_hook.read_key(key=file, bucket_name="korramanikumar")
        lines = file_data.strip().split('\n')
        for line in lines[1:]:  # Skip the header line
            date, client, sales = line.strip().split(',')
            combined_data.append([date, client, sales, filename])

    # Write combined data to a single CSV file
    with open("combined_data.csv", "w") as f:
        f.write("Date,Client,Sales in Million,File Name\n")
        for row in combined_data:
            f.write(",".join(row) + "\n")

    # Upload the file to S3
    s3_hook.load_file(
        filename="combined_data.csv",
        key="transformated_data/combined_data.csv",
        bucket_name="korramanikumar"
    )

    # Delete the local combined data file
    os.remove("combined_data.csv")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 3),
    'retries': 1,
}

with DAG('log_data_from_s3', default_args=default_args, schedule_interval=None) as dag:
    log_data_task = PythonOperator(
        task_id='log_data_task',
        python_callable=log_file_data_from_s3,
        provide_context=True
    )

    log_data_task
