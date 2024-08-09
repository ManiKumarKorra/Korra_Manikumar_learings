import boto3
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
# Creating an S3 access object 
obj = boto3.client("s3")
s3 = boto3.resource('s3')
bucket = s3.Bucket('korramanikumar')
s3_hook = S3Hook(aws_conn_id="aws_conn")
objs = s3_hook.objects.filter(Prefix='WEB')
for obj in objs:
    pass
