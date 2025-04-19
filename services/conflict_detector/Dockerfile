# services/conflict_detector/Dockerfile

FROM python:3.11-slim
WORKDIR /app

# 1) bring in your scheduling library
COPY libs/scheduling      ./libs/scheduling
# 2) copy only the right requirements
COPY services/conflict_detector/requirements.txt ./

# 3) tell Python about it
ENV PYTHONPATH=/app/libs

RUN pip install --no-cache-dir -r requirements.txt

# 4) now copy the Flask app
COPY services/conflict_detector ./

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]