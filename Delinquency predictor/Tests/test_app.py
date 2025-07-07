import pytest
import json
import os
import sys

# Add the parent directory (where app.py is) to the Python path
# This allows pytest to import 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_app.app import app


@pytest.fixture
def client():
    """Configures the Flask app for testing."""
    app.config['TESTING'] = True
    # If your app needs a specific model path for testing, set it here
    # app.config['MODEL_PATH'] = '../naive_bayes_model.pkl' # Example if model is outside tests dir
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test the root endpoint to ensure it returns the welcome message."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Credit Risk Category Prediction API!" in response.data


def test_app_page(client):
    """Test the /app endpoint to ensure it renders the HTML page."""
    response = client.get('/app')
    assert response.status_code == 200
    assert b"<title>Credit Risk Category Prediction</title>" in response.data


def test_predict_endpoint_success(client):
    """
    Tests the /predict endpoint with valid input data.
    NOTE: For a truly meaningful test, use actual scaled data from your
    training/testing set that you know the expected outcome for.
    This example uses a generic all-zeros input as a placeholder
    to test the API's structural response.
    """
    # Define a sample input matching the 43 features exactly
    test_data = {
        'CreditScore': 0.0, 'FirstPaymentDate': 0.0, 'FirstTimeHomebuyer': 0.0,
        'MaturityDate': 0.0, 'MSA': 0.0, 'MIP': 0.0, 'Units': 0.0,
        'Occupancy': 0.0, 'OCLTV': 0.0, 'DTI': 0.0, 'OrigUPB': 0.0,
        'LTV': 0.0, 'OrigInterestRate': 0.0, 'Channel': 0.0, 'PPM': 0.0,
        'ProductType': 0.0, 'PropertyState': 0.0, 'PropertyType': 0.0,
        # Note: PropertyType appears twice as per your X.columns.tolist()
        'PostalCode': 0.0, 'LoanPurpose': 0.0, 'OrigLoanTerm': 0.0,
        'NumBorrowers': 0.0, 'SellerName': 0.0, 'ServicerName': 0.0,
        'EverDelinquent': 0.0, 'MonthsDelinquent': 0.0, 'MonthsInRepayment': 0.0,
        'MonthlyIncome': 0.0, 'InterestBurden': 0.0, 'LTV_Diff': 0.0,
        'MIP_Ratio': 0.0, 'MultipleBorrowers': 0.0, 'log_OrigUPB': 0.0,
        'log_DTI': 0.0, 'log_MIP': 0.0, 'OrigUPB.1': 0.0, 'DTI.1': 0.0,
        'OrigUPB DTI': 0.0, 'PCA_1': 0.0, 'PCA_2': 0.0, 'PCA_3': 0.0,
        'PCA_4': 0.0, 'PCA_5': 0.0
    }

    response = client.post('/predict', data=json.dumps(test_data), content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'prediction' in data
    assert isinstance(data['prediction'], int)
    assert 'probability_class_0' in data
    assert isinstance(data['probability_class_0'], float)
    assert 'probability_class_1' in data
    assert isinstance(data['probability_class_1'], float)

    # Optional: If you know what prediction to expect for all zeros (e.g., class 0)
    # assert data['prediction'] == 0


def test_predict_endpoint_missing_feature(client):
    """
    Tests the /predict endpoint with missing feature data, expecting a 400 error.
    """
    # Test data with one feature intentionally missing (e.g., 'CreditScore')
    test_data_incomplete = {
        'FirstPaymentDate': 0.0, 'FirstTimeHomebuyer': 0.0, 'MaturityDate': 0.0,
        'MSA': 0.0, 'MIP': 0.0, 'Units': 0.0, 'Occupancy': 0.0,
        'OCLTV': 0.0, 'DTI': 0.0, 'OrigUPB': 0.0, 'LTV': 0.0,
        'OrigInterestRate': 0.0, 'Channel': 0.0, 'PPM': 0.0,
        'ProductType': 0.0, 'PropertyState': 0.0, 'PropertyType': 0.0,
        'PostalCode': 0.0, 'LoanPurpose': 0.0, 'OrigLoanTerm': 0.0,
        'NumBorrowers': 0.0, 'SellerName': 0.0, 'ServicerName': 0.0,
        'EverDelinquent': 0.0, 'MonthsDelinquent': 0.0, 'MonthsInRepayment': 0.0,
        'MonthlyIncome': 0.0, 'InterestBurden': 0.0, 'LTV_Diff': 0.0,
        'MIP_Ratio': 0.0, 'MultipleBorrowers': 0.0, 'log_OrigUPB': 0.0,
        'log_DTI': 0.0, 'log_MIP': 0.0, 'OrigUPB.1': 0.0, 'DTI.1': 0.0,
        'OrigUPB DTI': 0.0, 'PCA_1': 0.0, 'PCA_2': 0.0, 'PCA_3': 0.0,
        'PCA_4': 0.0, 'PCA_5': 0.0
    }

    response = client.post('/predict', data=json.dumps(test_data_incomplete), content_type='application/json')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing feature in input data:' in data['error']


def test_predict_endpoint_empty_input(client):
    """
    Tests the /predict endpoint with empty input, expecting a 400 error or similar.
    """
    response = client.post('/predict', data=json.dumps({}), content_type='application/json')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing feature in input data:' in data['error']