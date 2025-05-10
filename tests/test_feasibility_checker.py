# tests/test_feasibility_checker.py

import pytest
import logging
from libs.scheduling.feasibility_checker import sessions_conflict

# replace the existing DummySession with:
class DummySession:
    def __init__(self, day, start, end):
        # store exactly the keys your function expects
        self._data = {"day": day, "start": start, "end": end}

    def __getitem__(self, key):
        return self._data[key]


def test_sessions_do_not_conflict():
    s1 = DummySession("Monday",   "08:00:00", "09:00:00")
    s2 = DummySession("Monday",   "09:00:00", "10:00:00")
    assert not sessions_conflict(s1, s2)


def test_sessions_conflict_same_time():
    s1 = DummySession("Tuesday",  "10:00:00", "11:00:00")
    s2 = DummySession("Tuesday",  "10:30:00", "11:30:00")
    assert sessions_conflict(s1, s2)