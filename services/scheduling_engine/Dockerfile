FROM python:3.11-slim
WORKDIR /app

# Copy your requirements first
COPY requirements.txt ./

# Copy the 'libs' folder so that pip can see ../libs/scheduling
COPY ../../libs ./libs

# Install dependencies (including the editable lib)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code itself
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]