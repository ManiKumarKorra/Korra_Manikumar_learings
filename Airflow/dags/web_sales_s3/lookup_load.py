from airflow.models import DAG, TaskInstance

from airflow.operators.python import PythonOperator

from airflow.exceptions import AirflowSkipException

from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

from airflow.utils.dates import datetime, date_range



from web_sales_s3.lookup_task import move_data_to_s3

import csv

import logging

from airflow.providers.amazon.aws.hooks.s3 import S3Hook


import os



DAG_ID="lookup_load"


AWS_CONN_ID = "aws_conn"


SOURCE_S3_BUCKET = "korramanikumar"





# SOURCE_S3_FILE_PATTERN = "Data/WEB-SALES-%s.csv" % datetime.now().strftime("%Y-%m-%d")


SOURCE_S3_FILE_PATTERN = "Data/LOOKUPS-%s*" % datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
# s3://korramanikumar/Data/LOOKUPS-2024-05-22-04.10.04.527000..csv
# SOURCE_S3_FILE_PATTERN = "Data/LOOKUPS-2024-05-22-04.10.04.527000.csv"

logging.info(f'this is my file format{SOURCE_S3_FILE_PATTERN}')

print(f'this is my file format{SOURCE_S3_FILE_PATTERN}')



# SOURCE_S3_FILE_PATTERN = 'Data/WEB-SALES-2024-05-15.*.csv'



# SOURCE_S3_FILE_PATTERN = 'Data/WEB-SALES-{}-*.csv'.format(current_date)





# ile_name = '.*DOM-%s.*[.]csv' % datetime.now().strftime("%Y-%m-%d")

SOURCE_S3_TEMP_DIR   = "/tmp"


DEST_S3_BUCKET = "korramanikumar"

DEST_S3_BUCKET_PATH = "transformated_data/"

DEST_S3_FILE_PATTERN = "lookup-%s.csv" % datetime.now().strftime("%Y-%m-%d")




SNOWFLAKE_CONN_ID = "snowflake_conn"

SNOWFLAKE_DATABASE = "airflow_db"

SNOWFLAKE_SCHEMA = "public"

SNOWFLAKE_TABLE= "LOOKUPS"

SNOWFLAKE_STAGE="web_sales/"

SNOWFLAKE_WAREHOUSE="COMPUTE_WH"


default_args = {

    'owner': 'airflow',

    'depends_on_past': False,

    'email_on_failure': False,

    'email_on_retry': False,


    "params": {

        # "dest_file_name": DEST_S3_FILE_PATTERN,

        # "dest_bucket_path": DEST_S3_BUCKET_PATH,

        # "dest_bucket_name": DEST_S3_BUCKET,

        # "fail_run": "{{ dag_run.conf['fail_run'] if dag_run else False }}",

        # "start_hour": "{{ dag_run.conf['start_hour'] if dag_run else '' }}",
        # "end_hour": "{{ dag_run.conf['end_hour'] if dag_run else '' }}",
         "schedule_interval" :'@hourly',
        # "start_date": "{{ dag_run.conf['start_date'] if dag_run else '' }}",
        # "end_date": "{{ dag_run.conf['end_date'] if dag_run else '' }}",
        # 'date_range': date_range(start_date=datetime(2024, 5, 1), end_date=datetime(2024, 5, 10))




    },

    'catchup': False

}



def download_from_s3(task_instance: TaskInstance, **kwargs):
    s3_hook = S3Hook(aws_conn_id="aws_conn")  # Assuming you have set up the AWS connection in Airflow
    # Initialize the variable
    try:
        # List keys matching the file pattern
        response = s3_hook.get_wildcard_key(bucket_name=SOURCE_S3_BUCKET, wildcard_key=SOURCE_S3_FILE_PATTERN)
        logging.info("the file name " , response)
        if response:
                key = response.key
                print(key)
                logging.info(key)
           
             
               
                download_path = os.path.join(SOURCE_S3_TEMP_DIR, os.path.basename(key))
                logging.info(f"The key is : {key}")
                logging.info(f"The download_path is : {download_path}")
                S3Hook(aws_conn_id="aws_conn").get_conn().download_file(SOURCE_S3_BUCKET, key, download_path)
                logging.info(f"Downloaded file: {key} to {download_path}")
                # downloaded_file_path = S3Hook(aws_conn_id="aws_conn").get_conn().download_file(SOURCE_S3_BUCKET, key, download_path)
                with open(download_path, 'r') as file:
                    file_content = file.read()
 
                task_instance.xcom_push(key='downloaded_file', value= file_content)
 
                           
        else:
            logging.info("No files found matching the pattern.")
   
 
    except Exception as ex:
        raise RuntimeError(f"Error downloading file from S3: {ex}")






def process_csv_file(task_instance: TaskInstance, **kwargs):

    # Pull the CSV data from XCom

    csv_data = task_instance.xcom_pull(task_ids="download_from_s3_task", key="downloaded_file")     


    # Check if data is not None

    if csv_data:

        # Log the content of the pulled file

        logging.info(f"CSV data pulled from XCom: {csv_data}")


        # Transform the CSV data

        transformed_data = []

        lines = csv_data.split('\n')  # Convert CSV data into a list of lines

        reader = csv.reader(lines)

        headers = next(reader)  # Get header row


        # Map the column names

        modified_headers = []

        name_count = 0

        for idx, header in enumerate(headers):

            if header == 'Date':

                modified_headers.append('File Date' if idx == 0 else 'Event Date')

            # elif header == 'Name':

            #     name_count += 1

            #     modified_headers.append('Branch Name' if name_count == 1 else 'Line Name')

            else:

                modified_headers.append(header)


        transformed_data.append(','.join(modified_headers))  # Write modified headers

        transformed_data.extend(lines[1:])  # Write remaining rows, excluding the header


        transformed_lookups = '\n'.join(transformed_data)

        task_instance.xcom_push(key='transformed_lookups_data', value=transformed_lookups)  

    else:

        logging.warning("No CSV data found in XCom.")




with DAG(

    DAG_ID,

    description="Copy data from  S3 bucket and load into snowflake 'lookups' table",

    default_args=default_args,

    start_date=datetime(2024, 5, 25, 0, 0, 0),

    schedule_interval='@hourly',

    # template_searchpath="/dags/includes/sql/public/",

    catchup=False

) as dag:


    download_from_s3_task = PythonOperator(

        task_id="download_from_s3_task",

        python_callable=download_from_s3,

        provide_context=True,


    ) 


    process_csv_file_task = PythonOperator(

        task_id="process_csv_file_task",

        python_callable=process_csv_file,

        provide_context=True,

        #op_kwargs={},

    ) 


    move_data_to_s3_task = PythonOperator(

        task_id="move_data_to_s3_task",

        python_callable=move_data_to_s3,

        provide_context=True,

        op_kwargs={},

    )


    copy_s3_snowflake_to_lookups_table = SnowflakeOperator(

        task_id="copy_s3_snowflake_to_lookups_table",

        snowflake_conn_id=SNOWFLAKE_CONN_ID,

        sql="copy_s3_snowflake_to_lookups_table.sql",

        params={

            "database": SNOWFLAKE_DATABASE,

            "schema": SNOWFLAKE_SCHEMA,

            "table": SNOWFLAKE_TABLE,

            "stage": SNOWFLAKE_STAGE,

           },

        warehouse=SNOWFLAKE_WAREHOUSE,

        dag=dag

    )


    download_from_s3_task >> process_csv_file_task >> move_data_to_s3_task >> copy_s3_snowflake_to_lookups_table
