import pytest
from datetime import timedelta
from libs.scheduling.feasibility_checker import (
    parse_time,
    sessions_conflict,
    timetable_conflicts,
    generate_timetables_iterative,
    get_conflict_flags,
)

def test_parse_time_variants():
    # HH:MM:SS
    t1 = parse_time("09:15:00")
    assert t1.hour == 9 and t1.minute == 15
    # HH:MM
    t2 = parse_time("14:05")
    assert t2.hour == 14 and t2.minute == 5
    # timedelta
    td = timedelta(hours=8, minutes=30)
    t3 = parse_time(td)
    assert t3.hour == 8 and t3.minute == 30

def test_sessions_conflict_and_non_conflict():
    s1 = {"day":"Mon","start":"08:00:00","end":"09:00:00"}
    s2 = {"day":"Mon","start":"09:00:00","end":"10:00:00"}
    assert not sessions_conflict(s1,s2)
    s3 = {"day":"Mon","start":"08:30:00","end":"09:30:00"}
    assert sessions_conflict(s1,s3)
    # different day
    s4 = {"day":"Tue","start":"08:30:00","end":"09:30:00"}
    assert not sessions_conflict(s1,s4)

def test_timetable_conflicts():
    sec1 = {"sessions":[{"day":"Mon","start":"08:00:00","end":"09:00:00"}]}
    sec2 = {"sessions":[{"day":"Mon","start":"09:00:00","end":"10:00:00"}]}
    assert not timetable_conflicts([sec1,sec2])
    sec3 = {"sessions":[{"day":"Mon","start":"08:30:00","end":"09:30:00"}]}
    assert timetable_conflicts([sec1,sec3])

def test_generate_timetables_iterative():
    # Two courses, each with two non‑conflicting sections
    sections = [
      [{"cohort":"A","sessions":[{"day":"Mon","start":"08:00:00","end":"09:00:00"}]},
       {"cohort":"B","sessions":[{"day":"Mon","start":"09:00:00","end":"10:00:00"}]}],
      [{"cohort":"C","sessions":[{"day":"Mon","start":"10:00:00","end":"11:00:00"}]}]
    ]
    feas = generate_timetables_iterative(sections)
    # should get both combinations: A→C and B→C
    assert len(feas)==2
    assert any([c[0]["cohort"]=="A" for c in feas])
    assert any([c[0]["cohort"]=="B" for c in feas])

def test_get_conflict_flags_intra_and_inter():
    # two sections, each with two sessions
    sec1 = {"sessions":[
       {"day":"Mon","start":"08:00:00","end":"09:00:00"},
       {"day":"Mon","start":"08:30:00","end":"09:30:00"},
    ]}
    sec2 = {"sessions":[
       {"day":"Mon","start":"09:00:00","end":"10:00:00"},
    ]}
    flags = get_conflict_flags([sec1,sec2])
    # sec1 has an intra‑section conflict between its two sessions
    assert flags[0] == [True, True]
    # sec2’s session overlaps sec1’s second, so flagged
    assert flags[1] == [True]