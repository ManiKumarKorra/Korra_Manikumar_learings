"""Module shoppertrak_tasks - Shoppertrak tasks shared between DAGs."""
 
import logging
import tempfile
import os
import csv
 
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
 
from tools.s3_file_manager import S3FileManager
 
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
from datetime import datetime
 
S3_FILE_DATETIME_FORMAT = "%Y-%m-%d"
 
def move_data_to_s3(**context):
    """Function to move data to s3."""
    file_name = context["params"]["file_name"]
    bucket_path = context["params"]["bucket_path"]
    remote_bucket = context["params"]["bucket_name"]
    execution_date = context["execution_date"]

    s3_file_manager = S3FileManager(S3Hook("aws_conn"))

    task_instance = context["ti"]

    # Use the execution date from context
    from_datetime_string = execution_date.strftime(S3_FILE_DATETIME_FORMAT)

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_file = os.path.join(temp_dir, file_name % from_datetime_string)
        logging.info("Temporary CSV file: %s", tmp_file)

        # Retrieve CSV data from XCom
        csv_content_str = context["ti"].xcom_pull(task_ids="find_remote_csv_file", key="processed_csv_content")

        # Write CSV data to a temporary file
        with open(tmp_file, "w") as f:
            f.write(csv_content_str)

        # Upload the temporary CSV file to S3
        s3_file_manager.write_file_to_s3(
            local_file=tmp_file,
            remote_key=bucket_path + file_name % from_datetime_string,
            remote_bucket=remote_bucket,
            allow_replace=True
        )

    # the next task will use this to copy the s3 file to snowflake
    task_instance.xcom_push(key="s3_file_name", value=file_name % from_datetime_string)
