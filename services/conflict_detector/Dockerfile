FROM python:3.11-slim
WORKDIR /app

# 1) copy only requirements to leverage Docker cache
COPY requirements.txt ./

# 2) copy your libs into the image so pip can install it
COPY ../../libs/scheduling ./libs/scheduling

# 3) install everything (including your scheduling lib in editable mode)
RUN pip install --no-cache-dir -r requirements.txt

# 4) now copy the rest of your service code
COPY . .

# 5) expose & run (adjust port as needed)
EXPOSE 5002
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]