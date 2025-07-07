import os
import numpy as np
from flask import Flask, request, jsonify, render_template, g  # Added 'g' for request context
import joblib
import logging
import time  # Added for timing requests

# Prometheus client imports
from prometheus_client import generate_latest, Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Configure logging for the Flask application
logging.basicConfig(level=logging.INFO)

# Define the directory where app.py (and naive_bayes_model.pkl) resides
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the project's root directory (one level up from APP_DIR, where 'templates' is)
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))

# Initialize Flask app, explicitly setting the template folder using the PROJECT_ROOT
app = Flask(__name__, template_folder=os.path.join(PROJECT_ROOT, 'templates'))

# Define the model path relative to the APP_DIR (where app.py and model.pkl are)
MODEL_PATH = os.path.join(APP_DIR, 'naive_bayes_model.pkl')

model = None
try:
    model = joblib.load(MODEL_PATH)
    app.logger.info("Model loaded successfully!")
except FileNotFoundError:
    app.logger.error(f"Error: Model file '{MODEL_PATH}' not found. Please ensure it's in the correct directory.")
except Exception as e:
    app.logger.error(f"Error loading model: {e}")

# --- Prometheus Metrics Definitions ---
REQUESTS_TOTAL = Counter(
    'http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint']
)
REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds', 'HTTP request duration in seconds', ['method', 'endpoint']
)


# --- Flask Hooks for Metric Collection ---
@app.before_request
def before_request():
    """Records the start time of each request."""
    g.start_time = time.time()


@app.after_request
def after_request(response):
    """
    Records request metrics (total count and duration).
    Excludes the /metrics endpoint itself from being tracked.
    """
    if request.path != '/metrics':
        # Increment total requests counter
        REQUESTS_TOTAL.labels(request.method, request.path).inc()
        # Observe request duration
        response_time = time.time() - g.start_time
        REQUEST_DURATION_SECONDS.labels(request.method, request.path).observe(response_time)
    return response


# --- Flask Routes ---
@app.route('/')
def home():
    """Renders the home page with a welcome message."""
    return "Welcome to the Credit Risk Category Prediction API! Navigate to /app for the web interface."


@app.route('/app')
def web_app():
    """Renders the HTML web application form."""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles prediction requests. Expects JSON input with 43 features.
    Returns prediction and probabilities.
    """
    if model is None:
        app.logger.error("Prediction requested but model is not loaded.")
        return jsonify({'error': 'Internal server error: Model not loaded.'}), 500

    try:
        data = request.get_json(force=True)
        app.logger.info(f"Received raw input data: {data}")

        # Define the exact order of features expected by the model
        feature_order = [
            'CreditScore', 'FirstPaymentDate', 'FirstTimeHomebuyer', 'MaturityDate', 'MSA', 'MIP',
            'Units', 'Occupancy', 'OCLTV', 'DTI', 'OrigUPB', 'LTV', 'OrigInterestRate', 'Channel',
            'PPM', 'ProductType', 'PropertyState', 'PropertyType', 'PostalCode', 'LoanPurpose',
            'OrigLoanTerm', 'NumBorrowers', 'SellerName', 'ServicerName', 'EverDelinquent',
            'MonthsDelinquent', 'MonthsInRepayment', 'MonthlyIncome', 'InterestBurden', 'LTV_Diff',
            'MIP_Ratio', 'MultipleBorrowers', 'log_OrigUPB', 'log_DTI', 'log_MIP', 'OrigUPB.1',
            'DTI.1', 'OrigUPB DTI', 'PCA_1', 'PCA_2', 'PCA_3', 'PCA_4', 'PCA_5'
        ]

        # Create a list of feature values in the correct order
        ordered_features = [data[key] for key in feature_order]
        features_array = np.array(ordered_features).reshape(1, -1)

        app.logger.info(f"Processed features for prediction: {features_array}")

        prediction = model.predict(features_array)
        prediction_proba = model.predict_proba(features_array)

        # Assuming output classes are 0 (Low Risk) and 1 (High Risk)
        output = {
            'prediction': int(prediction[0]),
            'probability_class_0': float(prediction_proba[0][0]),
            'probability_class_1': float(prediction_proba[0][1])
        }
        app.logger.info(f"Prediction successful: {output}")
        return jsonify(output)

    except KeyError as ke:
        app.logger.error(f"KeyError: Missing expected feature in input data: {ke}", exc_info=True)
        return jsonify({'error': f'Missing feature in input data: {ke}. Please provide all 43 features.'}), 400
    except ValueError as ve:
        app.logger.error(f"ValueError during prediction (likely incorrect number or type of features): {ve}",
                         exc_info=True)
        return jsonify(
            {'error': f'Incorrect number or type of features provided. Please check input. Details: {ve}'}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500


# --- Prometheus WSGI Middleware ---
# This wraps the Flask app to expose the /metrics endpoint

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# --- Main entry point for running the Flask app ---
if __name__ == '__main__':
    # When running locally, Flask's built-in server is used.
    # In production (e.g., with Gunicorn via Docker), this block is not executed.
    app.run(debug=True, host='0.0.0.0', port=5000)