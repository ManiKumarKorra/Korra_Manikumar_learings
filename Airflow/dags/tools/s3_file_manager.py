"""Module s3_file_manager - managing the interaction with aws s3."""
 
import os
import logging
 
 
class S3FileManager:
    """Class representing an s3 file"""
    # 'S3Hook.get_conn().download_file()
 
    def __init__(self, s3_hook):
        self.s3_hook = s3_hook
 
    def download_file_from_s3_to_tmp(self, file_key, bucket, temp_dir):
        """Function to download data into a temp from s3."""
        try:
            downloaded_file = self.s3_hook.get_conn().download_file(
                key=file_key, local_path=temp_dir, bucket_name=bucket
            )
 
            return os.path.join(temp_dir, downloaded_file)
        except Exception as ex:
            logging.error("Error Downloading file: %s", (ex))
            raise
 
    def write_file_to_s3(
        self, local_file, remote_key, remote_bucket, allow_replace=False
    ):
        """Function to write data from local temp into s3."""
        try:
            # need to create your bucket on local stack first time round
            # self.s3_hook.create_bucket(remote_bucket)
 
            print("write_file_to_s3")
            print("remote_bucket: " + remote_bucket)
            print("remote_key: " + remote_key)
 
            # write_file_to_s3
            self.s3_hook.load_file(
                filename=local_file,
                key=remote_key,
                bucket_name=remote_bucket,
                replace=allow_replace,
                acl_policy="bucket-owner-full-control",
            )
 
        except Exception as ex:
            logging.error("Error uploading csv from temp storage to S3: %s", ex)
            raise
 
    def check_file_exists_on_s3(self, file_key, bucket):
        """Function to check if a file already exists in s3 bucket."""
        try:
            return self.s3_hook.check_for_key(key=file_key, bucket_name=bucket)
        except Exception as ex:
            logging.error("Error checking bucket for file key: %s", (ex))
            raise
 