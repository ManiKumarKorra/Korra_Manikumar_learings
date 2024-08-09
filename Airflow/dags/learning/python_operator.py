from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import datetime, timedelta
from airflow.operators.python import PythonOperator;

default_args ={
    'owner': 'KorraManikumar',
    'retries': 2,
    'retry_delay':timedelta(minutes=2)

}

def greet(ti,age):
    family_name = ti.xcom_pull(task_ids='get_name',key='family_name')
    sister_name = ti.xcom_pull(task_ids='get_name',key='sister_name')
    print(f" I am {age} years old.and my family name is {family_name} then my sister is {sister_name}")

def get_name(ti):
    ti.xcom_push(key="family_name",value="Korra")
    ti.xcom_push(key="sister_name",value="Vani")




with DAG(
    dag_id ="first_dag_using_pythonOperator",
    default_args=default_args,
    description='First DAG using BashOperator',
    start_date = datetime(2024,5,8,2),
    schedule_interval='@daily'
   
)as dag:
    task1 = PythonOperator(
        task_id="first_task",
        python_callable= greet,
        op_kwargs= {'name':'Manikumar', 'age':'23'}     
    )
    task2 = PythonOperator(
        task_id="get_name",
        python_callable=get_name
    )

task2>>task1