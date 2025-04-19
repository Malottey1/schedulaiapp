# services/web/Dockerfile

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# bring in scheduling if you need it
COPY libs/scheduling      ./libs/scheduling
# bring in your analytics helper
COPY services/analytics   ./services/analytics
# install deps
COPY services/web/requirements.txt ./
ENV PYTHONPATH=/app
RUN pip install --no-cache-dir -r requirements.txt

# now copy the web UI
COPY services/web         ./

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]