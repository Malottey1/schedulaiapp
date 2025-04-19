#!/usr/bin/env python3
from flask import Flask, jsonify, render_template
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
import os, logging


app = Flask(__name__)

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
    # Build grouped lecturer load data for summary and table:
    lecturer_load_groups = {"light": [], "moderate": [], "heavy": []}
    lecturer_load_table = []
    for (day, lecturer), minutes in load.items():
        # Add to table (this could be used for the interactive table)
        lecturer_load_table.append({"lecturer": lecturer, "day": day, "load": minutes})
        # Categorize load based on thresholds (Light: 0-90, Moderate: 91-180, Heavy: 181+)
        if minutes <= 90:
            lecturer_load_groups["light"].append({"lecturer": lecturer, "load": minutes})
        elif minutes <= 180:
            lecturer_load_groups["moderate"].append({"lecturer": lecturer, "load": minutes})
        else:
            lecturer_load_groups["heavy"].append({"lecturer": lecturer, "load": minutes})
    
    # Build pie chart data for lecturer load distribution.
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
        if room not in room_to_util:
            room_to_util[room] = {}
        room_to_util[room][day] = util
    utilization_by_day = []
    for room, day_utils in room_to_util.items():
        # Ensure each day is present (defaulting to 0 if missing)
        util_dict = {day: day_utils.get(day, 0) for day in days_order}
        utilization_by_day.append({'room': room, 'utilization': util_dict})
    
    # Build a summary grouping rooms by average utilization.
    utilization_summary = {'high': [], 'moderate': [], 'low': []}
    for item in utilization_by_day:
        room = item['room']
        utils = list(item['utilization'].values())
        avg_util = sum(utils) / len(utils) if utils else 0
        if avg_util >= 0.8:
            utilization_summary['high'].append(room)
        elif avg_util >= 0.5:
            utilization_summary['moderate'].append(room)
        else:
            utilization_summary['low'].append(room)
    
    # Build chart data for room utilization (one dataset per day).
    rooms_sorted = sorted(room_to_util.keys())
    datasets = []
    colors = {
        'Friday': '#007bff',      # Blue
        'Monday': '#28a745',      # Green
        'Tuesday': '#ffc107',     # Yellow
        'Wednesday': '#17a2b8',   # Teal
        'Thursday': '#dc3545'     # Red
    }
    for day in days_order:
        data = []
        for room in rooms_sorted:
            data.append(room_to_util.get(room, {}).get(day, 0))
        datasets.append({
            'label': day,
            'data': data,
            'backgroundColor': colors.get(day, '#6c757d')
        })
    room_util_chart_data = {
        'labels': rooms_sorted,
        'datasets': datasets
    }
    
    # Step 3: Compute overall score and grade.
    total_score, grade = grade_schedule(room_conflicts, lecturer_conflicts, utilization, load)
    
    # Step 4: Anomaly detection (e.g., overworked lecturers).
    anomalies = perform_anomaly_detection(load)
    
    # Step 5: Generate the analysis report using NLG (including conflict details).
    report = generate_analysis_report(total_score, grade, room_conflicts, lecturer_conflicts,
                                      utilization, load, room_conflict_details, lecturer_conflict_details)
    
    # Step 6: Generate visualizations (charts).
    room_util_img, lecturer_load_img = create_visualizations(utilization, load)
    
    # Render the analysis dashboard template, passing all computed variables.
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