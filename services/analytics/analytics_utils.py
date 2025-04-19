import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from jinja2 import Template
from sqlalchemy import create_engine
from urllib.parse import quote_plus



# ----------------------------------------------------
# Helper: Convert value to "HH:MM" string.
def convert_to_time(t):
    if isinstance(t, timedelta):
        # Convert timedelta to time by adding to datetime.min
        return (datetime.min + t).strftime("%H:%M")
    elif isinstance(t, str):
        # If it's already a string, assume "HH:MM" or "HH:MM:SS" and take first 5 characters.
        return t[:5]
    else:
        return str(t)

# ----------------------------------------------------
# Step 1: Load Timetable Data from the Staging Table
# ----------------------------------------------------
def get_timetable_data():
    password = "Naakey057@"
    encoded_password = quote_plus(password)  # Converts "@" to "%40"
    engine = create_engine(f'mysql+mysqlconnector://root:{encoded_password}@localhost/schedulai')
    query = """
    SELECT 
      sa.SessionID,
      sa.CourseCode,
      sa.SessionType,
      sa.LecturerName AS Lecturer,
      sa.CohortName,
      us.DayOfWeek,
      us.StartTime,
      us.EndTime,
      us.RoomName
    FROM SessionAssignments sa
    JOIN UpdatedSessionSchedule us ON sa.SessionID = us.SessionID
    ORDER BY sa.SessionID
    """
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        logging.error("Error fetching timetable data: " + str(e))
        return pd.DataFrame()

# ----------------------------------------------------
# Step 2: Evaluation Functions (Marking Scheme) with Conflict Details
# ----------------------------------------------------
def compute_conflicts(df):
    """
    Compute hard constraint violations by counting overlapping sessions per room and per lecturer.
    Returns:
      - room_conflict_count: total count of room conflicts
      - lecturer_conflict_count: total count of lecturer conflicts
      - room_conflict_details: list of dicts with details about each room conflict
      - lecturer_conflict_details: list of dicts with details about each lecturer conflict
    """
    room_conflict_details = []
    lecturer_conflict_details = []
    
    # Convert StartTime and EndTime into datetime objects using our helper.
    df['Start_dt'] = df['StartTime'].apply(lambda t: datetime.strptime(convert_to_time(t), "%H:%M"))
    df['End_dt'] = df['EndTime'].apply(lambda t: datetime.strptime(convert_to_time(t), "%H:%M"))
    
    # Room conflicts: group by Day and RoomName
    for (day, room), group in df.groupby(['DayOfWeek', 'RoomName']):
        sessions = group.sort_values('Start_dt')
        for i in range(len(sessions) - 1):
            current = sessions.iloc[i]
            next_sess = sessions.iloc[i + 1]
            if current['End_dt'] > next_sess['Start_dt']:
                room_conflict_details.append({
                    'day': day,
                    'room': room,
                    'conflict_between': [current['SessionID'], next_sess['SessionID']],
                    'current_end': current['End_dt'].strftime("%H:%M"),
                    'next_start': next_sess['Start_dt'].strftime("%H:%M")
                })
                
    # Lecturer conflicts: group by Day and Lecturer
    for (day, lecturer), group in df.groupby(['DayOfWeek', 'Lecturer']):
        sessions = group.sort_values('Start_dt')
        for i in range(len(sessions) - 1):
            current = sessions.iloc[i]
            next_sess = sessions.iloc[i + 1]
            if current['End_dt'] > next_sess['Start_dt']:
                lecturer_conflict_details.append({
                    'day': day,
                    'lecturer': lecturer,
                    'conflict_between': [current['SessionID'], next_sess['SessionID']],
                    'current_end': current['End_dt'].strftime("%H:%M"),
                    'next_start': next_sess['Start_dt'].strftime("%H:%M"),
                    'current_course': current['CourseCode'],
                    'next_course': next_sess['CourseCode'],
                    'current_cohort': current['CohortName'],
                    'next_cohort': next_sess['CohortName'],
                    'current_room': current['RoomName'],
                    'next_room': next_sess['RoomName'],
                    'current_session_type': current['SessionType'],
                    'next_session_type': next_sess['SessionType']
                })
                
    room_conflict_count = len(room_conflict_details)
    lecturer_conflict_count = len(lecturer_conflict_details)
    return room_conflict_count, lecturer_conflict_count, room_conflict_details, lecturer_conflict_details

def compute_room_utilization(df):
    """Compute utilization as fraction of available time booked.
       Assume available time per day is 540 minutes (from 08:00 to 17:00)."""
    total_minutes = 540
    utilization = {}
    for (day, room), group in df.groupby(['DayOfWeek', 'RoomName']):
        booked = 0
        for idx, row in group.iterrows():
            start = datetime.strptime(convert_to_time(row['StartTime']), "%H:%M")
            end = datetime.strptime(convert_to_time(row['EndTime']), "%H:%M")
            booked += (end - start).seconds / 60
        utilization[(day, room)] = booked / total_minutes
    return utilization

def compute_lecturer_load(df):
    """Compute total scheduled minutes per lecturer per day."""
    load = {}
    for (day, lecturer), group in df.groupby(['DayOfWeek', 'Lecturer']):
        total = 0
        for idx, row in group.iterrows():
            start = datetime.strptime(convert_to_time(row['StartTime']), "%H:%M")
            end = datetime.strptime(convert_to_time(row['EndTime']), "%H:%M")
            total += (end - start).seconds / 60
        load[(day, lecturer)] = total
    return load

def grade_schedule(room_conflicts, lecturer_conflicts, utilization, load):
    """Combine penalties from hard and soft constraints to assign a total score and letter grade.
       Lower score is better."""
    penalty = room_conflicts * 50 + lecturer_conflicts * 50
    # Soft constraint: ideally room utilization ~0.7
    util_penalty = sum([abs(u - 0.7) * 5 for u in utilization.values()])
    # Soft constraint: ideally lecturer load <= 270 minutes (4.5 hours) per day
    load_penalty = sum([max(0, l - 270) * 0.25 for l in load.values()])
    total_score = penalty + util_penalty + load_penalty
    if total_score <= 150:
        grade = "A"
    elif total_score <= 200:
        grade = "B"
    elif total_score <= 250:
        grade = "C"
    elif total_score <= 300:
        grade = "D"
    else:
        grade = "E"
    return total_score, grade

# ----------------------------------------------------
# Step 3: AI/ML – Anomaly Detection on Lecturer Load
# ----------------------------------------------------
def perform_anomaly_detection(load):
    """Uses k-means clustering on lecturer load to flag potential overwork.
       Returns a DataFrame of anomalies."""
    df_load = pd.DataFrame(list(load.items()), columns=['Day_Lecturer', 'Load'])
    if df_load.empty:
        return df_load
    kmeans = KMeans(n_clusters=3, random_state=0)
    df_load['Cluster'] = kmeans.fit_predict(df_load[['Load']])
    # Identify which cluster has the higher average load
    cluster_means = df_load.groupby('Cluster')['Load'].mean()
    overworked_cluster = cluster_means.idxmax()
    anomalies = df_load[df_load['Cluster'] == overworked_cluster]
    return anomalies

# ----------------------------------------------------
# Step 3: Generate an Analysis Report (NLG)
# ----------------------------------------------------
def generate_analysis_report(total_score, grade, room_conflicts, lecturer_conflicts, utilization, load,
                             room_conflict_details, lecturer_conflict_details):
    template_str = """
    <h2>Timetable Analysis Report</h2>
    <p><strong>Hard Constraint Violations:</strong></p>
    <ul>
      <li>Room Conflicts: {{ room_conflicts }} 
          {% if room_conflict_details|length > 0 %}
            <ul>
            {% for conflict in room_conflict_details %}
              <li>Day: {{ conflict.day }}, Room: {{ conflict.room }}, 
                  Conflict between sessions {{ conflict.conflict_between[0] }} and {{ conflict.conflict_between[1] }},
                  (Ends at {{ conflict.current_end }}, Starts at {{ conflict.next_start }})</li>
            {% endfor %}
            </ul>
          {% endif %}
      </li>
      <li>Lecturer Conflicts: {{ lecturer_conflicts }} 
          {% if lecturer_conflict_details|length > 0 %}
            <ul>
            {% for conflict in lecturer_conflict_details %}
              <li>Day: {{ conflict.day }}, Lecturer: {{ conflict.lecturer }}, 
                  Conflict between sessions {{ conflict.conflict_between[0] }} and {{ conflict.conflict_between[1] }},
                  (Ends at {{ conflict.current_end }}, Starts at {{ conflict.next_start }})</li>
            {% endfor %}
            </ul>
          {% endif %}
      </li>
    </ul>
    <p><strong>Overall Evaluation:</strong></p>
    <ul>
      <li>Total Score: {{ total_score }}</li>
      <li>Assigned Grade: {{ grade }}</li>
    </ul>
    """
    template = Template(template_str)
    return template.render(
        room_conflicts=room_conflicts,
        lecturer_conflicts=lecturer_conflicts,
        total_score=total_score,
        grade=grade,
        utilization=utilization,
        load=load,
        room_conflict_details=room_conflict_details,
        lecturer_conflict_details=lecturer_conflict_details
    )

# ----------------------------------------------------
# Step 4: Visualization Dashboard (Generate Charts)
# ----------------------------------------------------
def create_visualizations(utilization, load):
    # Room Utilization Chart
    fig1, ax1 = plt.subplots(figsize=(8,4))
    room_keys = [f"{day} - {room}" for (day, room) in utilization.keys()]
    util_vals = list(utilization.values())
    ax1.barh(room_keys, util_vals)
    ax1.set_xlabel("Utilization Fraction")
    ax1.set_title("Room Utilization")
    buf1 = io.BytesIO()
    plt.tight_layout()
    fig1.savefig(buf1, format='png')
    buf1.seek(0)
    room_util_img = base64.b64encode(buf1.getvalue()).decode('utf8')
    plt.close(fig1)

    # Lecturer Load Chart
    fig2, ax2 = plt.subplots(figsize=(8,4))
    lecturer_keys = [f"{day} - {lecturer}" for (day, lecturer) in load.keys()]
    load_vals = list(load.values())
    ax2.barh(lecturer_keys, load_vals, color='orange')
    ax2.set_xlabel("Minutes")
    ax2.set_title("Lecturer Load")
    buf2 = io.BytesIO()
    plt.tight_layout()
    fig2.savefig(buf2, format='png')
    buf2.seek(0)
    lecturer_load_img = base64.b64encode(buf2.getvalue()).decode('utf8')
    plt.close(fig2)

    return room_util_img, lecturer_load_img