# Credit Risk Predictor with Monitoring

This project implements a simple Flask-based web application for predicting credit delinquency, with integrated monitoring using Prometheus and Grafana.

## Table of Contents

-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Project Structure](#project-structure)
-   [Local Setup and Running the Application](#local-setup-and-running-the-application)
    -   [1. Clone the Repository](#1-clone-the-repository)
    -   [2. Build the Docker Image](#2-build-the-docker-image)
    -   [3. Run the Flask Application (Docker Container)](#3-run-the-flask-application-docker-container)
    -   [4. Set up Prometheus for Monitoring](#4-set-up-prometheus-for-monitoring)
    -   [5. Set up Grafana for Visualization](#5-set-up-grafana-for-visualization)
-   [Accessing the Application and Monitoring](#accessing-the-application-and-monitoring)
-   [Deployment (Optional)](#deployment-optional)

## Features

* **Flask Web Application:** A simple interface to input financial details and get a credit delinquency prediction.
* **Naive Bayes Model:** Uses a pre-trained `naive_bayes_model.pkl` for predictions.
* **Dockerized:** The application is containerized using Docker for easy setup and consistent environments.
* **Prometheus Monitoring:** Integrates `prometheus_client` to expose application metrics (e.g., HTTP request counts, durations).
* **Grafana Dashboards:** Visualize real-time application performance and usage metrics.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Git:** For cloning the repository.
    * [Download Git](https://git-scm.com/downloads)
* **Docker Desktop:** For building and running the application container.
    * [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
* **Prometheus:** The time-series database for collecting metrics.
    * [Download Prometheus](https://prometheus.io/download/) (Choose the latest stable release for your OS)
* **Grafana:** The open-source platform for data visualization and analysis.
    * [Download Grafana](https://grafana.com/grafana/download/) (Choose the latest stable release for your OS)

## Project Structure
.
├── Dockerfile                  # Defines the Docker image for the Flask app
├── flask_app/
│   ├── init.py
│   ├── app.py                  # Main Flask application with Prometheus instrumentation
│   └── naive_bayes_model.pkl   # Pre-trained Naive Bayes model
├── templates/
│   └── index.html              # HTML template for the web interface
├── requirements.txt            # Python dependencies (Flask, Gunicorn, scikit-learn, prometheus_client etc.)
└── prometheus.yml              # Prometheus configuration file to scrape Flask app metrics


## Local Setup and Running the Application

Follow these steps to get the entire application and monitoring stack running on your local machine.

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone [YOUR_GITHUB_REPO_URL]
cd Your-Repo-Name # Replace Your-Repo-Name with the actual folder name
Replace [YOUR_GITHUB_REPO_URL] with the actual URL of your GitHub repository.

2. Build the Docker Image
Navigate to the root directory of your cloned project (where Dockerfile is located) in your terminal and build the Docker image:

Bash

docker build -t credit-risk-predictor .
This command builds the Docker image named credit-risk-predictor. This might take a few minutes on the first run.

3. Run the Flask Application (Docker Container)
Ensure Docker Desktop is running. Then, from your project's root directory in the terminal, run the Docker container:

Bash

docker run -p 5000:5000 credit-risk-predictor
This starts your Flask application inside a Docker container, mapping port 5000 from the container to port 5000 on your host machine. Keep this terminal window open.

4. Set up Prometheus for Monitoring
Prometheus will collect metrics from your running Flask application.

a.  Unzip Prometheus:
* Download and unzip the Prometheus archive. You will likely find a folder named something like prometheus-X.Y.Z.windows-amd64 (the version number will vary) containing prometheus.exe and a default prometheus.yml.
* For simplicity, you can move this entire unzipped Prometheus folder directly into your project's root directory, or keep it anywhere convenient.

b.  Configure prometheus.yml:
* Navigate into the unzipped Prometheus folder (e.g., cd prometheus-X.Y.Z.windows-amd64).
* Make sure the prometheus.yml file in this specific Prometheus folder has the following content:
```yaml
global:
scrape_interval: 15s # How frequently Prometheus will scrape targets
evaluation_interval: 15s # How frequently Prometheus will evaluate rules

    scrape_configs:
      - job_name: 'flask_app'
        static_configs:
          - targets: ['localhost:5000'] # Your Flask app's host and port
            labels:
              application: 'DelinquencyPredictor'
    ```
c.  Run Prometheus:
* Open a new terminal or command prompt window (separate from your Docker app).
* Navigate to the specific directory where prometheus.exe is located (e.g., cd C:\Users\YourUser\YourProject\prometheus-X.Y.Z.windows-amd64 or wherever you placed it).
* Run Prometheus:
bash ./prometheus.exe --config.file=prometheus.yml 
* Keep this terminal window open. Prometheus will be accessible at http://localhost:9090.

5. Set up Grafana for Visualization
Grafana will visualize the metrics collected by Prometheus.

a.  Install Grafana:
* Download and install Grafana for your operating system. It typically runs as a background service.

b.  Access Grafana:
* Open your web browser and go to: http://localhost:3000
* Default login: admin / admin (you'll be prompted to change the password).

c.  Add Prometheus as a Data Source:
* In Grafana's left-hand menu, hover over the gear icon (Configuration) and click "Data sources".
* Click "Add data source" and select "Prometheus".
* Set the URL to http://localhost:9090.
* Click "Save & Test". You should see "Data source is working."

d.  Create a Simple Dashboard (Optional):
* In the left-hand menu, hover over the "+" icon (Create) and click "Dashboard".
* Click "Add a new panel".
* In the "Query" tab, select your Prometheus data source and enter a PromQL query, e.g., http_requests_total for total requests, or rate(http_requests_total[1m]) for requests per second.
* Adjust panel title and visualization type (e.g., "Stat" or "Graph"). Click "Apply."
* Save your dashboard.

Accessing the Application and Monitoring
Once all components are running:

Flask Application: Open your web browser and go to: http://localhost:5000/app

Flask Metrics: View raw metrics at: http://localhost:5000/metrics

Prometheus UI: Access Prometheus's own web interface at: http://localhost:9090

Grafana Dashboards: View your custom dashboards at: http://localhost:3000
