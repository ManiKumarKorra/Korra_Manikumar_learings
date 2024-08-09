from airflow.models import DagBag
from airflow.utils.dates import days_ago

dag_id = 'lookup_loadtest'
start_date = '2024-05-01'
end_date = '2024-05-30'

# Load the DAG
dag_bag = DagBag()
dag = dag_bag.get_dag(dag_id)

# Perform the backfill
if dag:
    dag.backfill(
        start_date=days_ago(1),  # Start date can be set to any date within the desired range
        end_date=days_ago(0),    # End date can be set to any date within the desired range
        ignore_first_depends_on_past=True,
        include_adhoc=False,
        donot_pickle=True,
        reset_dag_run=False,
    )
else:
    print(f"DAG '{dag_id}' not found.")
