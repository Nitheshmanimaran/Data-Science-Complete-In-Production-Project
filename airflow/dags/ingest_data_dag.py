from datetime import datetime
from datetime import timedelta
import pandas as pd
import great_expectations as ge
from great_expectations.core.batch import BatchRequest
import warnings
warnings.filterwarnings("ignore")
import logging
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago


@dag(
    dag_id='ingest_data_dag',
    description='Dag which will check for data quality with great_expectations and ingest data',
    tags=['data_checking', 'data_ingestion', 'great_expectations'],
    schedule=timedelta(minutes=2),
    start_date=days_ago(n=0, hour=1)
)


def ingest_data():

    @task
    def get_data_to_ingest_from_local_file() -> pd.DataFrame:
        nb_rows = 5
        filepath = '/d/EPITA/dsp/flight_v3/dsp-project-dsp-flight/airflow/input_data/Flights50.csv'
        input_data_df = pd.read_csv(filepath)
        logging.info(f'Extract {nb_rows} from the file {filepath}')
        data_to_ingest_df = input_data_df.sample(n=nb_rows)
        return data_to_ingest_df

    @task
    def save_data(data_to_ingest_df: pd.DataFrame) -> str:
        file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
        filepath = f'/d/EPITA/dsp/flight_v3/dsp-project-dsp-flight/airflow/folder_A/{file}'
        data_to_ingest_df.to_csv(filepath, index=False)
        return file
            
    @task
    def validate_data(file, data_to_ingest_df: pd.DataFrame):
        context = ge.data_context.DataContext()
        
        expectation_suite_name = "one"
        batch_request = {
            'datasource_name': 'my_datasource',
            'data_connector_name': 'default_inferred_data_connector_name',
            'data_asset_name': file,
            'limit': 1000}
        
        validator = context.get_validator(
            batch_request=BatchRequest(**batch_request),
            expectation_suite_name= expectation_suite_name
            )
        
        results = validator.validate()
        
        if results['success'] == True:
            logging.info(f'Validation succeeded')
            filepath = f'/d/EPITA/dsp/flight_v3/dsp-project-dsp-flight/airflow/folder_C/{file}'
            data_to_ingest_df.to_csv(filepath, index=False)

        elif results['success'] == False:
            logging.info(f'Validation failed')
            filepath = f'/d/EPITA/dsp/flight_v3/dsp-project-dsp-flight/airflow/folder_B/{file}'
            data_to_ingest_df.to_csv(filepath, index=False)
            
        else:
            logging.info(f'Validation failed')
            
    data_to_ingest_df = get_data_to_ingest_from_local_file()
    file = save_data(data_to_ingest_df)
    validate_data(file, data_to_ingest_df)

ingest_data_dag = ingest_data()
