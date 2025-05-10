# tests/test_scheduler.py
import pytest
import pandas as pd
import libs.scheduling.scheduler as schedmod
from libs.scheduling.scheduler import schedule_sessions

@pytest.fixture
def sample_session_csv(tmp_path):
    header = "SessionID,CourseCode,LecturerName,CohortName,SessionType,Duration,NumberOfEnrollments,AdditionalStaff\n"
    rows = [
        "1330,AS111,Facilitator A,Section A,Discussion,01:00:00,15,None",
        "1331,AS111,Facilitator B,Section B,Discussion,01:00:00,15,None",
        "1332,AS111,Facilitator C,Section C,Discussion,01:00:00,15,None",
        "1333,AS111,Facilitator D,Section D,Discussion,01:00:00,15,None",
        "1334,AS111,Facilitator E,Section E,Discussion,01:00:00,15,None",
        "1335,AS111,Facilitator F,Section F,Discussion,01:00:00,15,None",
        "1336,AS111,Facilitator G,Section G,Discussion,01:00:00,15,None",
        "1337,AS111,Facilitator H,Section H,Discussion,01:00:00,15,None",
        "1338,AS111,Facilitator I,Section I,Discussion,01:00:00,15,None",
        "1339,AS111,Facilitator J,Section J,Discussion,01:00:00,15,None",
        "1340,AS111,Facilitator K,Section K,Discussion,01:00:00,15,None",
        "1341,AS111,Facilitator L,Section L,Discussion,01:00:00,15,None",
    ]
    path = tmp_path / "SessionAssignments.csv"
    path.write_text(header + "".join(r + "\n" for r in rows))
    return str(path)

@pytest.fixture
def sample_prefs_csv(tmp_path):
    prefs = """Course Code - Course Name,Location,Session Type
AS111 - Ashesi Success,Jackson Lab 221,Seminar
AS111 - Ashesi Success,Jackson Lab 222,Seminar
AS111 - Ashesi Success,Apt Hall 216,Seminar
AS111 - Ashesi Success,Nutor Hall 216,Seminar
AS111 - Ashesi Success,Bio Lab,Seminar
AS111 - Ashesi Success,Science Lab,Seminar
AS111 - Ashesi Success,Norton-Motulsky 207A,Seminar
AS111 - Ashesi Success,Fab Lab 103,Seminar
AS111 - Ashesi Success,Fab Lab 203,Seminar
AS111 - Ashesi Success,Fab Lab 303,Seminar
AS111 - Ashesi Success,Nutor Hall 115,Seminar
BUSA432 - Organisational Development,Radichel MPR,Lecture
BUSA432 - Organisational Development,Radichel MPR,Discussion
BUSA432 - Organisational Development,Apt Hall 216,Lecture
BUSA432 - Organisational Development,Jackson Hall 115,Discussion
BUSA132 - Organizational Behaviour,Jackson Lab 221,Lecture
BUSA132 - Organizational Behaviour,Nutor Hall 100,Discussion
"""
    path = tmp_path / "SessionLocationPreferences.csv"
    path.write_text(prefs)
    return str(path)

def test_schedule_sessions_includes_all_ids(monkeypatch, sample_session_csv, sample_prefs_csv):
    # 1) Build simple rooms_df (one big room)
    rooms_df = pd.DataFrame([{"RoomID":1, "Location":"AnyRoom", "MaxRoomCapacity":100}])

    # 2) sessions_df from your CSV
    sessions_df = pd.read_csv(sample_session_csv)

    # 3) preferences_df from your prefs CSV
    #    the code in fetch_data expects columns: CourseCode, Location, SessionType
    prefs_raw = pd.read_csv(sample_prefs_csv)
    # split "Course Code - Course Name" into CourseCode
    prefs_raw["CourseCode"] = prefs_raw["Course Code - Course Name"].str.split(" - ").str[0]
    session_preferences_df = prefs_raw[["CourseCode", "Location", "Session Type"]].rename(
        columns={"Session Type": "SessionType"}
    )

    # 4) monkey‑patch fetch_data to return our three dataframes
    def fake_fetch_data(path):
        return sessions_df, rooms_df, session_preferences_df
    monkeypatch.setattr(schedmod, "fetch_data", fake_fetch_data)

    # 5) capture the final write without touching real DB
    captured = {}
    def fake_write_schedule_to_db(assigned):
        captured["assigned"] = assigned
    monkeypatch.setattr(schedmod, "write_schedule_to_db", fake_write_schedule_to_db)

    # 6) run!
    schedule_sessions(sample_session_csv)

    # 7) assert
    assert "assigned" in captured, "Scheduler never called write_schedule_to_db()"
    assigned_list = captured["assigned"]
    returned_ids = { s["Session ID"] for s in assigned_list }
    assert returned_ids == set(range(1330, 1342)), f"got {returned_ids}"