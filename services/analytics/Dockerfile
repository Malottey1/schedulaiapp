FROM python:3.11-slim
WORKDIR /app

# copy only its requirements
COPY services/analytics/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of service code
COPY services/analytics ./

EXPOSE 5003
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5003"]