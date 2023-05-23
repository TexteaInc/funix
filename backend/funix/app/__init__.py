"""
Save the app instance here
"""

from secrets import token_hex

import flask
from flask_cors import CORS

app = flask.Flask(__name__)
app.secret_key = token_hex(16)
CORS(app)
