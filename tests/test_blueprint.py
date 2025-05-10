import pytest
from flask import Flask
import libs.scheduling.feasibility_checker as fc

@pytest.fixture
def client(monkeypatch):
    # stub GA endpoint
    monkeypatch.setattr(fc, "genetic_algorithm_feasibility_check", 
        lambda max_generations=0,population_size=0: {
            (1,"X"): {
               "courses": ["C1"],
               "feasible_timetables": [
                 [{"cohort":"C1","course_code":"C1","sessions":[{"day":"Mon","start":"09:00:00","end":"10:00:00"}]}]
               ],
               "conflict_timetables": []
            }
        })
    app = Flask(__name__)
    app.register_blueprint(fc.feasibility_bp)
    return app.test_client()

def test_feasibility_endpoint_returns_html(client):
    rv = client.get("/feasibility_check")
    assert rv.status_code == 200
    assert b"C1" in rv.data  # your rendered template should include the course code