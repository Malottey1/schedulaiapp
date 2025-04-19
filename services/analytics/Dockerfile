# Use a slim official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any) and Python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Expose the port for the analytics service
EXPOSE 5003

# Run the Flask app with Gunicorn in production mode
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5003"]