FROM python:3.11-slim
WORKDIR /app

# 1) your scheduling lib
COPY libs/scheduling ./libs/scheduling

# 2) install requirements
COPY services/conflict_detector/requirements.txt ./
ENV PYTHONPATH=/app/libs
RUN pip install --no-cache-dir -r requirements.txt prometheus_client

# 3) copy the app code
COPY services/conflict_detector ./

# 4) conflict_detector’s own templates
COPY services/conflict_detector/templates ./templates

# 5) pull in the shared base.html from the web service
COPY services/web/templates/base.html ./templates/

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]