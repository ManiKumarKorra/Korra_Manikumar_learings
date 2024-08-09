from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import requests
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 29),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'citibike_pull_data_s3_push',
    default_args=default_args,
    description='DAG to pull data from Citibike API using XCom and push to S3',
    schedule_interval='@daily',
)

def pull_data_from_api_and_push_to_xcom(**kwargs):
    api_url = "https://jsonplaceholder.typicode.com/posts/1"
    response = requests.get(api_url)
    
    # Check if the response is successful
    if response.status_code == 200:
        try:
            data = response.json()
            print("Data retrieved from API:", data)  # Add this line for logging
        except json.decoder.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            data = None
    else:
        print("Error: API request failed with status code", response.status_code)
        data = None
    
    # Push the data to XCom
    kwargs['ti'].xcom_push(key='citibike_data', value=data)

def push_to_s3(**kwargs):
    s3_conn_id = "aws_conn"
    
    # Pull the data from XCom
    data = kwargs['ti'].xcom_pull(task_ids='pull_data_from_api_and_push_to_xcom', key='citibike_data')

    # Push the data to S3
    s3_hook = S3Hook(aws_conn_id=s3_conn_id)
    s3_bucket_name = "korramanikumar"
    s3_key = "Data/citibike_station_information.json"
    s3_hook.load_string(json.dumps(data), s3_key, bucket_name=s3_bucket_name, replace=True)

pull_data_task = PythonOperator(
    task_id='pull_data_from_api_and_push_to_xcom',
    python_callable=pull_data_from_api_and_push_to_xcom,
    provide_context=True,
    dag=dag,
)

push_to_s3_task = PythonOperator(
    task_id='push_to_s3',
    python_callable=push_to_s3,
    provide_context=True,
    dag=dag,
)

pull_data_task >> push_to_s3_task
