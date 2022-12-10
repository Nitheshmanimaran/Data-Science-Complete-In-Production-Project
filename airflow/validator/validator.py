# Validation file using Great Expectations for the data ingestion
import pandas as pd
import great_expectations as ge
from great_expectations.core.batch import BatchRequest
import warnings
warnings.filterwarnings('ignore')

context = ge.data_context.DataContext()
expectation_suite_name = "one"

def validate_data(file):
    batch_request = {
        'datasource_name': 'my_datasource',
        'data_connector_name': 'default_inferred_data_connector_name',
        'data_asset_name': file,
        'limit': 1000}
    validator = context.get_validator(
        batch_request=BatchRequest(**batch_request),
        expectation_suite_name=expectation_suite_name
    )

    results = validator.validate()
    # Getting the success of the validation
    if results['success']:
        return True
    else:
        return False        
