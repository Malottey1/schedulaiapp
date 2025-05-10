import pytest
import libs.scheduling.feasibility_checker as fc

def test_expand_electives_plain():
    assert fc.expand_electives("CS101", 42)==["CS101"]

def test_expand_electives_all(monkeypatch):
    # placeholder ELECTIVE returns whatever fetch_all_electives_codes gives
    monkeypatch.setattr(fc, "fetch_all_electives_codes", lambda: ["X1","Y2"])
    assert set(fc.expand_electives("ELECTIVE", 1))=={"X1","Y2"}

def test_expand_electives_major_and_nonmajor(monkeypatch):
    monkeypatch.setattr(fc, "fetch_all_electives_codes", lambda: ["CS101","MATH101","BUSA101"])
    monkeypatch.setattr(fc, "get_student_major_prefixes", lambda sid: ["CS"])
    majors   = fc.expand_electives("ELECTIVE1", 7)
    nonmajors= fc.expand_electives("ELECTIVE2", 7)
    assert majors   == ["CS101"]
    assert set(nonmajors)=={"MATH101","BUSA101"}