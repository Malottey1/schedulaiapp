FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY services/web/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY services/web ./

EXPOSE 5000
CMD ["gunicorn", "-k", "eventlet", "app:app", "--bind", "0.0.0.0:5000"]