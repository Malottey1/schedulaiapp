#!/usr/bin/env python3
import os
import logging
import threading
from flask import Flask, request, redirect, url_for, flash, render_template
from scheduling.scheduler import schedule_sessions as run_schedule

# ----------------------------------------------------
# App & Logging setup
# ----------------------------------------------------
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "change-me")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s"
)
app.logger.setLevel(logging.INFO)

# ----------------------------------------------------
# ROUTE: Run Scheduler (background thread)
# ----------------------------------------------------
@app.route('/run_scheduler', methods=['GET', 'POST'])
def run_scheduler():
    app.logger.info("Accessed /run_scheduler route.")
    if request.method == 'POST':
        # path to your CSV or whatever input the scheduler needs
        session_csv = os.path.join(
            os.path.dirname(__file__),
            'scheduling',
            'Session_Location_Preferences.csv'
        )
        try:
            scheduler_thread = threading.Thread(
                target=run_schedule,
                args=(session_csv,)
            )
            scheduler_thread.daemon = True
            scheduler_thread.start()
            flash("Scheduling started in the background.", "success")
            app.logger.info("Scheduler thread started.")
        except Exception as e:
            flash(f"Error scheduling: {e}", "danger")
            app.logger.error(f"Scheduler failed: {e}")
        return redirect('/timetable')

    # GET → render a simple form
    return render_template('run_scheduler.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port)