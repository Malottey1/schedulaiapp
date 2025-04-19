# Base image
FROM python:3.11-slim

# Prevent Python buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port your Flask app listens on
EXPOSE 5000

# Use Gunicorn with the Eventlet worker for SocketIO support
CMD ["gunicorn", "-k", "eventlet", "app:app", "--bind", "0.0.0.0:5000"]