#!/usr/bin/env python3
import os
import logging
import threading
import time
from flask import Flask, request, redirect, url_for, flash, render_template, g
from scheduling.scheduler import schedule_sessions as run_schedule
from prometheus_client import make_wsgi_app, Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Response

# ----------------------------------------------------
# App & Logging setup
# ----------------------------------------------------
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "change-me")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s"
)
app.logger.setLevel(logging.INFO)

# ----------------------------------------------------
# Prometheus Metrics
# ----------------------------------------------------
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latency of HTTP requests in seconds',
    ['method', 'endpoint']
)
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)

@app.before_request
def _start_timer():
    g.start_time = time.time()

@app.after_request
def _record_request_data(response):
    resp_time = time.time() - g.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(resp_time)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

# ----------------------------------------------------
# ROUTE: Run Scheduler (background thread)
# ----------------------------------------------------
@app.route('/run_scheduler', methods=['GET', 'POST'])
def run_scheduler():
    app.logger.info("Accessed /run_scheduler route.")
    if request.method == 'POST':
        session_csv = os.path.join(
            os.path.dirname(__file__),
            'scheduling',
            'Session_Location_Preferences.csv'
        )
        try:
            scheduler_thread = threading.Thread(
                target=run_schedule,
                args=(session_csv,)
            )
            scheduler_thread.daemon = True
            scheduler_thread.start()
            flash("Scheduling started in the background.", "success")
            app.logger.info("Scheduler thread started.")
        except Exception as e:
            flash(f"Error scheduling: {e}", "danger")
            app.logger.error(f"Scheduler failed: {e}")
        return redirect('/timetable')

    return render_template('run_scheduler.html')

# ----------------------------------------------------
# Expose Prometheus metrics at /metrics
# ----------------------------------------------------
# Option 1: WSGI dispatcher
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# Option 2: direct endpoint (if preferred)
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
