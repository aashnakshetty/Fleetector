from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "aashna",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="fleetector_disruption_monitor",
    default_args=default_args,
    description="Hourly Quick-Commerce Delivery Disruption ETL Pipeline",
    start_date=datetime(2026, 11, 14),
    schedule="@hourly",
    catchup=False,
) as dag:

    run_etl_task = BashOperator(
        task_id="fetch_and_load_disruptions",
        bash_command="python /opt/airflow/scripts/fetch_disruptions.py",
    )