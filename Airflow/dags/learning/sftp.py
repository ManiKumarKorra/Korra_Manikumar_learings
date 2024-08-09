from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook  # Import S3Hook
import paramiko
import csv  # Import csv module

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
    'sftp_to_xcom',
    default_args=default_args,
    description='DAG to pull data from SFTP server and push to XCom',
    schedule_interval=None,  # Removed schedule_interval for manual triggering
)

def pull_data_from_sftp_and_push_to_xcom(**kwargs):
    # Connect to SFTP server
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='eu-central-1.sftpcloud.io', username='4e558948b95d48dca1fdd334d74b298e', password='oKv3rxNLYdXbhzPAusKD6F2GTaFkj8Ik')
    
    # Download file from SFTP server
    sftp_client = ssh_client.open_sftp()
    remote_path = '/Sample100csv.csv'
    
    # Read the file content
    try:
        with sftp_client.open(remote_path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File {remote_path} not found on SFTP server.")
    
    sftp_client.close()
    
    # Decode the data using 'latin-1' encoding
    decoded_data = data.decode('latin-1')
    
    # Push the data to XCom
    kwargs['ti'].xcom_push(key='sftp_data', value=decoded_data)

def push_to_s3(**kwargs):
    s3_conn_id = "aws_conn"
    data = kwargs['ti'].xcom_pull(task_ids='pull_data_from_sftp_and_push_to_xcom', key='sftp_data')
    s3_hook = S3Hook(aws_conn_id=s3_conn_id)
    s3_bucket_name = "korramanikumar"
    s3_key = "Data/sftp.csv"
    s3_hook.load_string(str(data), s3_key, bucket_name=s3_bucket_name, replace=True)


pull_sftp_data_task = PythonOperator(
    task_id='pull_data_from_sftp_and_push_to_xcom',
    python_callable=pull_data_from_sftp_and_push_to_xcom,
    provide_context=True,
    dag=dag,
)

push_to_s3_task = PythonOperator(
    task_id='push_to_s3',
    python_callable=push_to_s3,
    provide_context=True,
    dag=dag,
)

pull_sftp_data_task >> push_to_s3_task  # Correct task dependency
