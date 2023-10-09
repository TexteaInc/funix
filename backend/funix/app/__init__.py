"""
Save the app instance here
"""

from secrets import token_hex

import flask

app = flask.Flask(__name__)
app.secret_key = token_hex(16)
app.config.update(
    SESSION_COOKIE_PATH="/",
    SESSION_COOKIE_SAMESITE="Lax",
)


@app.after_request
def funix_auto_cors(response: flask.Response) -> flask.Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    return response
