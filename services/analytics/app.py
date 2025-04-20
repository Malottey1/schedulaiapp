#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, g, Response
from prometheus_client import make_wsgi_app, Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from analytics_utils import (
    get_timetable_data,
    compute_conflicts,
    compute_room_utilization,
    compute_lecturer_load,
    grade_schedule,
    perform_anomaly_detection,
    generate_analysis_report,
    create_visualizations
)
import os, logging, time

app = Flask(__name__)

# ────────────────────────────────────────────────────────────────────────────────
# Prometheus metrics definition & instrumentation
# ────────────────────────────────────────────────────────────────────────────────
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
    elapsed = time.time() - g.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(elapsed)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
# ────────────────────────────────────────────────────────────────────────────────

# ----------------------------------------------------
# Flask Endpoint: /analyze_timetable
# ----------------------------------------------------
@app.route('/analyze_timetable', methods=['GET'])
def analyze_timetable():
    # Step 1: Load data
    df = get_timetable_data()
    if df.empty:
        return "No timetable data available.", 500

    # Step 2: Evaluate conflicts and soft constraints.
    room_conflicts, lecturer_conflicts, room_conflict_details, lecturer_conflict_details = compute_conflicts(df)
    utilization = compute_room_utilization(df)
    load = compute_lecturer_load(df)
    
    # --- Compute Lecturer Load Context ---
    lecturer_load_groups = {"light": [], "moderate": [], "heavy": []}
    lecturer_load_table = []
    for (day, lecturer), minutes in load.items():
        lecturer_load_table.append({"lecturer": lecturer, "day": day, "load": minutes})
        if minutes <= 90:
            lecturer_load_groups["light"].append({"lecturer": lecturer, "load": minutes})
        elif minutes <= 180:
            lecturer_load_groups["moderate"].append({"lecturer": lecturer, "load": minutes})
        else:
            lecturer_load_groups["heavy"].append({"lecturer": lecturer, "load": minutes})
    
    lecturer_load_pie_data = {
        "labels": ["Light", "Moderate", "Heavy"],
        "data": [
            len(lecturer_load_groups["light"]),
            len(lecturer_load_groups["moderate"]),
            len(lecturer_load_groups["heavy"])
        ]
    }
    
    # --- Compute Room Utilization Context ---
    days_order = ['Friday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
    room_to_util = {}
    for (day, room), util in utilization.items():
        room_to_util.setdefault(room, {})[day] = util
    utilization_by_day = []
    for room, day_utils in room_to_util.items():
        util_dict = {day: day_utils.get(day, 0) for day in days_order}
        utilization_by_day.append({'room': room, 'utilization': util_dict})
    
    utilization_summary = {'high': [], 'moderate': [], 'low': []}
    for item in utilization_by_day:
        avg_util = sum(item['utilization'].values()) / len(days_order)
        if avg_util >= 0.8:
            utilization_summary['high'].append(item['room'])
        elif avg_util >= 0.5:
            utilization_summary['moderate'].append(item['room'])
        else:
            utilization_summary['low'].append(item['room'])
    
    rooms_sorted = sorted(room_to_util.keys())
    datasets = []
    colors = {
        'Friday': '#007bff',
        'Monday': '#28a745',
        'Tuesday': '#ffc107',
        'Wednesday': '#17a2b8',
        'Thursday': '#dc3545'
    }
    for day in days_order:
        data = [room_to_util.get(room, {}).get(day, 0) for room in rooms_sorted]
        datasets.append({'label': day, 'data': data, 'backgroundColor': colors.get(day)})
    room_util_chart_data = {'labels': rooms_sorted, 'datasets': datasets}
    
    # Step 3: Score & grade
    total_score, grade = grade_schedule(room_conflicts, lecturer_conflicts, utilization, load)
    anomalies = perform_anomaly_detection(load)
    report = generate_analysis_report(
        total_score, grade, room_conflicts, lecturer_conflicts,
        utilization, load, room_conflict_details, lecturer_conflict_details
    )
    room_util_img, lecturer_load_img = create_visualizations(utilization, load)
    
    return render_template("analysis_dashboard.html",
                           report=report,
                           grade=grade,
                           total_score=total_score,
                           room_util_img=room_util_img,
                           lecturer_load_img=lecturer_load_img,
                           anomalies=anomalies.to_dict(orient="records"),
                           room_conflict_details=room_conflict_details,
                           lecturer_conflict_details=lecturer_conflict_details,
                           utilization_by_day=utilization_by_day,
                           utilization_summary=utilization_summary,
                           room_util_chart_data=room_util_chart_data,
                           lecturer_load_groups=lecturer_load_groups,
                           lecturer_load_table=lecturer_load_table,
                           lecturer_load_pie_data=lecturer_load_pie_data)

# Mount Prometheus WSGI app
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})