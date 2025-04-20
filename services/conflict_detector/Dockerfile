FROM python:3.11-slim
WORKDIR /app

# your scheduling lib
COPY libs/scheduling ./libs/scheduling

# install requirements
COPY services/conflict_detector/requirements.txt ./
ENV PYTHONPATH=/app/libs
RUN pip install --no-cache-dir -r requirements.txt

# copy the app code
COPY services/conflict_detector ./

# copy in the templates
COPY services/conflict_detector/templates ./templates

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]