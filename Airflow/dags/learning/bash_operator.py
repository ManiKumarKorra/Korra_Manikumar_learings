# from airflow import DAG
# from airflow.operators.bash_operator import BashOperator
# from airflow.utils.dates import datetime, timedelta


# default_args ={
#     'owner': 'KorraManikumar',
#     'retries': 2,
#     'retry_delay':timedelta(minute=2)

# }

# with DAG(
#     dag_id ="first_dag_using_bash",
#     default_args=default_args,
#     description='First DAG using BashOperator',a
#     start_date = datetime(2024,5,8,2),
#     schedule_interval='@daily'
   
# )as dag:
#     task1 = BashOperator(
#         task_id="first_task",
#         bash_command="echo hello world"
#     )


# task1
