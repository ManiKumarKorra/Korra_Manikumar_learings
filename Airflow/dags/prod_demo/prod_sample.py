from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
 
def add_date_column_to_csv(bucket_name, object_key, **kwargs):
    s3_hook = S3Hook(aws_conn_id='aws_conn')
    
    # Check if the object exists before performing any operations
    if not s3_hook.check_for_key(object_key, bucket_name):
        # Handle the case where the object does not exist
        print(f"The object with key '{object_key}' does not exist in the bucket '{bucket_name}'.")
        return
    
    # Read the content of the existing object
    csv_content = s3_hook.read_key(object_key, bucket_name)
    
    # Extract date from filename
    filename = object_key.split('/')[-1]  # Extract filename from object_key
    date_str = filename.split('_')[1].split('.')[0]  # Extract date from filename

    # Process each line and add date as the fourth column
    processed_lines = [
        ','.join(line.split(',') + [date_str])
        for line in csv_content.strip().split('\n')
    ]
    
    # Join the processed lines back into CSV content
    transformed_csv_content = '\n'.join(processed_lines)
    
    # Modify object key to include the new file name
    new_object_key = object_key.replace("DailyReport", "transformed_DailyReport")

    # Upload the transformed content with the modified object key
    s3_hook.load_string(
        transformed_csv_content,
        new_object_key,
        bucket_name
    )

 
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 5, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
 
with DAG('override_csv_dag', default_args=default_args, schedule_interval='@daily') as dag:
    transform_task = PythonOperator(
        task_id='add_date_column_to_csv',
        python_callable=add_date_column_to_csv,
        op_kwargs={'bucket_name': 'korramanikumar', 'object_key': 'prod_test/DailyReport_2024-05-07.csv'}
    )
 
    transform_task  # No dependencies as we're directly transforming and storing in S3
    