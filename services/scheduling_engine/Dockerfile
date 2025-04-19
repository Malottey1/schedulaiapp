FROM python:3.11-slim
WORKDIR /app

# 1) copy requirements
COPY services/scheduling_engine/requirements.txt ./

# 2) copy your shared library
COPY libs/scheduling ./libs/scheduling

# 3) install deps (including the editable install)
RUN pip install --no-cache-dir -r requirements.txt

# 4) copy only your service code
COPY services/scheduling_engine ./

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]