"""
Save the app instance here
"""

import flask
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)
