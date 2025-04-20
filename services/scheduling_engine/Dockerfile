# services/scheduling_engine/Dockerfile

FROM python:3.11-slim
WORKDIR /app

COPY libs/scheduling      ./libs/scheduling
COPY services/scheduling_engine/requirements.txt ./

ENV PYTHONPATH=/app/libs

RUN pip install --no-cache-dir -r requirements.txt prometheus_client
COPY services/scheduling_engine ./

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]