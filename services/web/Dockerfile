# services/web/Dockerfile
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 1) bring in your scheduling lib
COPY libs/scheduling ./libs/scheduling

# 2) install everything
COPY services/web/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3) copy the rest of the web app
COPY services/web ./

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]