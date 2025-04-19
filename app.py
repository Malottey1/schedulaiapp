#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import re
import threading
import os
import logging
import json
from datetime import datetime, timedelta, time
from collections import defaultdict
import random
from sklearn.cluster import KMeans
import numpy as np
import pygad
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import matplotlib.pyplot as plt
import io
import re
import base64
from jinja2 import Template
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from flask_socketio import SocketIO, emit
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename



# Local module imports
# Import the feasibility blueprint and function from the scheduling package.
from scheduling.feasibility_checker import feasibility_bp, generate_all_feasible_timetables_with_conflicts



app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with a secure secret key

# Initialize SocketIO with the Flask app
socketio = SocketIO(app)

# Register the feasibility blueprint with an appropriate URL prefix.
# Here we register it at the root so that endpoints like /feasibility_check are available.


    










































