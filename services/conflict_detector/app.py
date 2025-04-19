#!/usr/bin/env python3
import os
import logging
from flask import Flask, redirect, url_for
from scheduling.feasibility_checker import feasibility_bp

# ----------------------------------------------------
# App & Logging setup
# ----------------------------------------------------
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s"
)

# ----------------------------------------------------
# Register feasibility blueprint
# ----------------------------------------------------
app.register_blueprint(feasibility_bp, url_prefix='/')

# ----------------------------------------------------
# Convenience endpoint to redirect to the blueprint’s /feasibility_check
# ----------------------------------------------------
@app.route('/feasibility', methods=['GET'])
def feasibility():
    # Assuming your blueprint defines a function named `feasibility_check`
    return redirect(url_for('feasibility.feasibility_check'))

# ----------------------------------------------------
# Main runner
# ----------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002))
    app.run(host='0.0.0.0', port=port)