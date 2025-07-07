# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# This step is done early to leverage Docker's caching,
# so dependencies are only reinstalled if requirements.txt changes.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container at /app
# This includes flask_app/, templates/, and naive_bayes_model.pkl
COPY . /app

# Expose port 5000 for the Flask application
EXPOSE 5000

# Run gunicorn to serve the Flask application
# It looks for the 'app' object inside the 'app' module within the 'flask_app' package
CMD ["gunicorn", "flask_app.app:app", "-b", "0.0.0.0:5000"]