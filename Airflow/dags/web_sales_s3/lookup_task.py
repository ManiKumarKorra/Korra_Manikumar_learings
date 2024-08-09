"""Module rex_lookups_tasks - lookups tasks shared between DAGs."""


import logging

import tempfile

import os


from airflow.providers.amazon.aws.hooks.s3 import S3Hook


from tools.s3_file_manager import S3FileManager


logging.basicConfig()

logging.getLogger().setLevel(logging.DEBUG)


S3_FILE_DATETIME_FORMAT = "%Y-%m-%d"



def move_data_to_s3(**context):

    """Function to move data to s3."""

    dest_s3_file_name = context["params"]["dest_file_name"]

    dest_s3_bucket_path  = context["params"]["dest_bucket_path"]

    dest_s3_bucket_name = context["params"]["dest_bucket_name"]



    s3_file_manager = S3FileManager(S3Hook("aws_conn"))


    task_instance = context["ti"]


    # from_datetime_string = data_s3_interval_start.strftime(

    #     S3_FILE_DATETIME_FORMAT

    # )


    with tempfile.TemporaryDirectory() as temp_dir:

        tmp_file = os.path.join(temp_dir, dest_s3_file_name)

        logging.info(

            "This is the tmp file: %s", tmp_file

        )

        lookups_data_str = context["ti"].xcom_pull(task_ids='process_csv_file_task', key="transformed_lookups_data")

        with open(tmp_file, 'w') as f:

           f.write(lookups_data_str)

        s3_file_manager.write_file_to_s3(

            local_file=tmp_file,

            remote_key= dest_s3_bucket_path + dest_s3_file_name,

            remote_bucket=dest_s3_bucket_name,

            allow_replace=True

        )


    # the next task will use this to copy the s3 file to snowflake

    task_instance.xcom_push(key="s3_lookup_file_name", value=dest_s3_file_name)