from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from datetime import datetime
import csv
 
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 13),
    'retries': 1,
}
 
def modify_csv_columns(source_bucket, source_key, destination_bucket, destination_key, **kwargs):
    s3_hook = S3Hook(aws_conn_id='aws_conn')
 
    # Read CSV content
    csv_data = s3_hook.read_key(source_key, bucket_name=source_bucket)
 
    # Modify column names
    modified_csv_lines = []
    lines = csv_data.split('\n')  # Convert CSV data into a list of lines
    reader = csv.reader(lines)
    headers = next(reader)  # Get header row
 
    # Map the column names
    modified_headers = []
    name_count = 0
    for idx, header in enumerate(headers):
        if header == 'Date':
            modified_headers.append('file_date' if idx == 0 else 'Date')
        elif header == 'Name':
            name_count += 1
            modified_headers.append('branch_name' if name_count == 1 else 'line_name')
        else:
            modified_headers.append(header)
 
    modified_csv_lines.append(','.join(modified_headers))  # Write modified headers
    modified_csv_lines.extend(lines[1:])  # Write remaining rows, excluding the header
 
    modified_csv_content = '\n'.join(modified_csv_lines)
 
    # Write modified CSV content to destination S3 bucket
    s3_hook.load_string(
        string_data=modified_csv_content,
        key=destination_key,
        bucket_name=destination_bucket
    )
    print("Modified CSV file written to destination S3 bucket.")
 
with DAG('modify_csv_columns', default_args=default_args, schedule_interval=None) as dag:
    modify_csv_task = PythonOperator(
        task_id='modify_csv_columns',
        python_callable=modify_csv_columns,
        op_kwargs={
            'source_bucket': 'korramanikumar',
            'source_key': 'Data/column_change-2024-05-14.csv',
            'destination_bucket': 'korramanikumar',
            'destination_key': 'transformated_data/destination_file.csv'
        }
    )

# Set task dependencies
modify_csv_task
