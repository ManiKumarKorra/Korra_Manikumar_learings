from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.hooks.S3_hook import S3Hook

from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator
import csv

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 6),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

dag = DAG(
    'copy_csv_to_snowflake1',
    default_args=default_args,
    description='Copy CSV file from source S3 bucket to destination S3 bucket and then load to Snowflake table',
    schedule_interval=None,
)

source_bucket_name = 'korramanikumar'
source_key = 'test/APR_2020.csv'  # Update file name here
destination_bucket_name = 'korramanikumar'
destination_key_prefix = 'test'
snowflake_table_name = 'sales_data'

def add_upload_date_to_csv(**kwargs):
    source_bucket = kwargs.get('source_bucket')
    source_key = kwargs.get('source_key')
    destination_bucket = kwargs.get('destination_bucket')
    destination_key_prefix = kwargs.get('destination_key_prefix')

    # Get S3 hook
    s3_hook = S3Hook(aws_conn_id='aws_conn')

    # Read the CSV file from source S3
    csv_content = s3_hook.read_key(source_key, source_bucket)

    # Add file upload date to each row
    upload_date = datetime.utcnow().strftime('%Y-%m-%d')
    original_file_name = source_key.split("/")[-1].split(".")[0]  # Extract original file name without extension
    destination_key = f'{destination_key_prefix}/{original_file_name}-{upload_date}.csv'

    lines = csv_content.split('\n')
    modified_lines = []
    for i, line in enumerate(lines):
        if i == 0:  # Add the header for the first line
            modified_lines.append(line.strip() + ',load_date')
        elif i < len(lines) - 1:  # Exclude adding upload date to the last line
            modified_lines.append(line.strip() + ',' + upload_date)
        else:
            modified_lines.append(line.strip())  # Just append the last line without modification

    # Write modified CSV to temporary file
    modified_csv_content = '\n'.join(modified_lines)

    # Upload modified CSV to destination S3 with upload date in the file name
    s3_hook.load_string(
        modified_csv_content,
        destination_key,
        bucket_name=destination_bucket,
        replace=True
    )

# Define tasks
copy_to_destination_s3_task = PythonOperator(
    task_id='copy_to_destination_s31',
    python_callable=add_upload_date_to_csv,
    op_kwargs={
        'source_bucket': source_bucket_name,
        'source_key': source_key,
        'destination_bucket': destination_bucket_name,
        'destination_key_prefix': destination_key_prefix,
    },
    dag=dag,
)

load_to_snowflake_task = SnowflakeOperator(
    task_id='load_to_snowflake1',
    snowflake_conn_id='snowflake_conn',
    sql=f"""
        COPY INTO sales_data
        FROM @transformated_data
        PATTERN='.*APR_2020-2024-05-07.csv'
        FILE_FORMAT = (FORMAT_NAME = my_csv_format)
        ON_ERROR = CONTINUE;  -- Adjust error handling as needed
    """,
    dag=dag,
)

copy_to_destination_s3_task >> load_to_snowflake_task
