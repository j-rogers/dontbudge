"""Dashboard

The dashboard is the main web interface of the DontBudge app.

Author: Josh Rogers (2021)
"""
from flask import Blueprint

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

from dontbudge.dashboard import routes