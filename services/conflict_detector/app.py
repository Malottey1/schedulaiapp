#!/usr/bin/env python3
import os
import logging
import time
from flask import Flask, redirect, url_for, flash, request, g, Response
from scheduling.feasibility_checker import feasibility_bp
from prometheus_client import Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# ----------------------------------------------------
# App & Logging setup
# ----------------------------------------------------
app = Flask(__name__, template_folder="templates")
app.logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s"
)

# ----------------------------------------------------
# Prometheus instrumentation
# ----------------------------------------------------
# define your metrics
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

# record start time before each request
@app.before_request
def _start_timer():
    g.start_time = time.time()

# observe metrics after each request
@app.after_request
def _record_request_data(response):
    resp_time = time.time() - g.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(resp_time)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

# integrate Prometheus WSGI app on /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# ----------------------------------------------------
# Register feasibility blueprint
# ----------------------------------------------------
app.register_blueprint(feasibility_bp, url_prefix='/')

# ----------------------------------------------------
# Convenience stubs for sidebar endpoints
# ----------------------------------------------------
@app.route('/feasibility', methods=['GET'])
def feasibility():
    return redirect(url_for('feasibility.feasibility_check'))

@app.route('/conflicts')
def conflicts():
    return redirect('/conflicts')

@app.route('/resolve_room_conflicts')
def resolve_room_conflicts():
    return redirect('/resolve_room_conflicts')

@app.route('/manage_sessions_schedule')
def manage_sessions_schedule():
    return redirect('/manage_sessions_schedule')

@app.route('/analyze_timetable')
def analyze_timetable():
    return redirect('/analyze_timetable')

@app.route('/conflict_free_matrix')
def conflict_free_matrix():
    return redirect('/conflict_free_matrix')

@app.route('/student_timetables')
def student_timetables():
    return redirect('/student_timetables')

@app.route('/timetable')
def timetable():
    return redirect('/timetable')

@app.route('/export_csv')
def export_csv():
    return redirect('/export_csv')

@app.route('/dashboard')
def dashboard():
    return redirect('/dashboard')

# ----------------------------------------------------
# Main runner
# ----------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002))
    app.run(host='0.0.0.0', port=port)
