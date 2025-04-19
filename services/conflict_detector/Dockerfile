# services/conflict_detector/Dockerfile

FROM python:3.11-slim
WORKDIR /app

# 1) Copy and install requirements
COPY services/conflict_detector/requirements.txt ./
# 2) Copy in your local scheduling lib
COPY libs/scheduling ./libs/scheduling

RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy the rest of your service code
COPY services/conflict_detector ./

EXPOSE 5002
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]