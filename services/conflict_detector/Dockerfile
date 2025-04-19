# Use a slim Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY . .

# Expose the port your Flask app listens on
EXPOSE 5002

# Run under Gunicorn for production
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5002"]