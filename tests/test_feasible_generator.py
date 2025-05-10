# In tests/test_feasible_generator.py

import pytest
from libs.scheduling.feasibility_checker import (
    generate_all_feasible_timetables_with_conflicts,
    # … other imports …
)

def test_generate_all_feasible(monkeypatch):
    import libs.scheduling.feasibility_checker as fc

    # stub out student selections
    monkeypatch.setattr(
        fc,
        "fetch_student_course_selections",
        lambda: {(1, "A"): ["0", "1"]}
    )

    # each course expands to itself
    monkeypatch.setattr(fc, "expand_electives", lambda code, sid: [code])

    # both courses have the exact same 08:00–09:00 session → always conflict
    monkeypatch.setattr(
        fc,
        "fetch_sections_for_course",
        lambda code: [
            {
                "cohort": code,
                "sessions": [{"day": "Mon", "start": "08:00:00", "end": "09:00:00"}]
            }
        ]
    )

    all_res = generate_all_feasible_timetables_with_conflicts()

    # Should have an entry for (1,"A")
    assert (1, "A") in all_res

    data = all_res[(1, "A")]
    feasibles = data["feasible_timetables"]
    conflicts = data["conflict_timetables"]

    # Expect no feasible but exactly one conflicting combination
    assert feasibles == [], f"Expected no feasible timetables, got {len(feasibles)}"
    assert len(conflicts) == 1, f"Expected 1 conflict timetable, got {len(conflicts)}"