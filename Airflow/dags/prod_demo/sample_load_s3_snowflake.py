from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator


# file_name = "DOM-2024-05-13-04.09.31.946000.csv" 

# file_name = "DOM-%s" % datetime.now().strftime("%Y-%m-%d")

actually = 'DOM-2024-05-17.*[.]csv'

file_name = 'DOM-%s.*[.]csv' % datetime.now().strftime("%Y-%m-%d")




# file_name = "DOM-%s-*.csv" % datetime.now().strftime("%Y-%m-%d")

# file_name = "'DOM-' || to_char(current_date, 'YYYY-MM-DD') || '-%.csv'"

# file_name =fr"DOM-{datetime.now().strftime('%Y-%m-%d')}-*.csv"

# file_name = "DOM-%s{*}.csv" % datetime.now().strftime("%Y-%m-%d")


# file_name = f"DOM-{datetime.now().strftime('%Y-%m-%d')}*.csv"
#file_name = "DOM-{}*.csv".format(datetime.now().strftime("%Y-%m-%d"))


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    's3_to_snowflake',
    default_args=default_args,
    description='A DAG to copy CSV file from S3 to Snowflake',
    schedule_interval='@daily',
    start_date=datetime(2024, 5, 6),
    template_searchpath="dags/includes/sql/public/",
    catchup=False
)

copy_s3_to_snowflake_dom_orders_table = SnowflakeOperator(
    task_id="copy_s3_to_snowflake_dom_orders_table",
    snowflake_conn_id='snowflake_conn',  # Replace 'snowflake_conn' with your Snowflake connection ID
    sql="copy_s3_to_snowflake_dom_orders_table.sql",
    params={
        "database": 'airflow_db',  # Replace 'airflow_db' with your database name
        "schema": 'public',  # Replace 'public' with your schema name
        "table": 'data',  # Replace 'sales_data' with your table name
        "pattern": file_name,
        "stage": 'airflow_db.public.manhattan',  # Replace 'MANHATTAN' with your Snowflake stage name
        
    },
    warehouse='COMPUTE_WH',  # Replace 'COMPUTE_WH' with your Snowflake warehouse name
    dag=dag
)

copy_s3_to_snowflake_dom_orders_table


