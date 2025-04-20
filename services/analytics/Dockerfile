FROM python:3.11-slim
WORKDIR /app

# 1) Install Python deps (including prometheus_client)
COPY services/analytics/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt prometheus_client

# 2) Copy the analytics service code
COPY services/analytics ./

# 3) Expose the HTTP port
EXPOSE 5003

# 4) Launch with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5003", "app:app"]