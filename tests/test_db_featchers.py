import pytest
from libs.scheduling.feasibility_checker import (
    fetch_all_electives_codes,
    fetch_sections_for_course,
    get_student_major_prefixes
)

class DummyCursor:
    def __enter__(self): return self
    def __exit__(self,*_) : pass
    def execute(self, q, p): pass
    def fetchone(self): return {"MajorID":2}
    def fetchall(self): 
        if "FROM Course" in self._last_query:
            return [{"CourseCode":"AA"},{"CourseCode":"BB"}]
        return []
    @property
    def _last_query(self): return self.last_q
    def execute(self, q,p):
        self.last_q=q

class DummyConn:
    def cursor(self, dictionary=True):
        return DummyCursor()
    def close(self): pass

@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    import libs.scheduling.feasibility_checker as fc
    monkeypatch.setattr(fc, "get_db_connection", lambda: DummyConn())

def test_get_student_major_prefixes():
    # DummyCursor.fetchone returns MajorID=2 → prefixes ["CS"]
    from libs.scheduling.feasibility_checker import get_student_major_prefixes
    assert get_student_major_prefixes(123)==["CS"]

def test_fetch_all_electives_codes():
    codes = fetch_all_electives_codes()
    assert codes==["AA","BB"]

def test_fetch_sections_for_course():
    # make cursor.fetchall return two session rows
    class SectionCursor(DummyCursor):
        def fetchall(self):
            return [
               {"CohortName":"X","DayOfWeek":"Tue","StartTime":"08:00:00","EndTime":"09:00:00"},
               {"CohortName":"X","DayOfWeek":"Wed","StartTime":"10:00:00","EndTime":"11:00:00"},
            ]
    monkeypatch = pytest.MonkeyPatch()
    def fake_conn(): return DummyConn()
    # swap get_db_connection to return conn whose cursor is SectionCursor
    import libs.scheduling.feasibility_checker as fc
    monkeypatch.setattr(fc, "get_db_connection", lambda: DummyConn())
    monkeypatch.setattr(DummyConn, "cursor", lambda self, dictionary=True: SectionCursor())
    sections = fetch_sections_for_course("ANY")
    assert len(sections)==1
    sec = sections[0]
    assert sec["cohort"]=="X"
    assert len(sec["sessions"])==2
    monkeypatch.undo()