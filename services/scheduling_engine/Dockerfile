# Use a slim Python base
FROM python:3.11-slim

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code (including templates/)
COPY . .

# Expose the scheduler port
EXPOSE 5001

# Run under Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5001"]