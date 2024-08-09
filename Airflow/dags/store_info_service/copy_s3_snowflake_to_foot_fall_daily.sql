COPY INTO {{ params.database }}.{{ params.schema }}.{{ params.table }}
FROM @{{ params.stage }}
FILE_FORMAT = ( type='csv', trim_space = true, field_delimiter = ',', escape_unenclosed_field=none, encoding='ISO-8859-1' )
PATTERN='.*{{ ti.xcom_pull(key="s3_file_name") }}'
ON_ERROR=continue;