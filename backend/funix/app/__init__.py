"""
Save the app instance here
"""
import json
import os
import re
from datetime import datetime, timezone
from secrets import token_hex

from flask import Flask, Response, abort, request
from flask_sock import Sock
from sqlalchemy import create_engine, text
from sqlalchemy.pool import SingletonThreadPool

app = Flask(__name__)
app.secret_key = token_hex(16)
app.config.update(
    SESSION_COOKIE_PATH="/",
    SESSION_COOKIE_SAMESITE="Lax",
)
sock = Sock(app)


@app.after_request
def funix_auto_cors(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


if os.environ.get("DISABLE_FUNIX_TELEMETRY") is None:
    telemetry_db = os.environ.get("FUNIX_TELEMETRY_DB", default="sqlite:///logs.db")
    engine = create_engine(telemetry_db, poolclass=SingletonThreadPool)
    with engine.connect() as con:
        create_table = """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_time TEXT NOT NULL,
                request TEXT NOT NULL,
                response TEXT NOT NULL
            );
            """
        con.execute(text(create_table))
        con.commit()

    @app.after_request
    def funix_logger(response: Response) -> Response:
        global con

        do_not_log_me = request.cookies.get("DO_NOT_LOG_ME")
        if do_not_log_me is not None and do_not_log_me == "YES":
            return response

        try:
            req_json = request.json
        except:
            return response

        if req_json is None:
            return response

        try:
            resp_json = response.json
        except:
            return response

        if resp_json is None:
            return response

        dumped_req = json.dumps(
            {
                "url": request.url,
                "headers": dict(request.headers),
                "data": req_json,
            }
        )

        dumped_resp = json.dumps(resp_json)

        with engine.connect() as con:
            con.execute(
                text(
                    "INSERT INTO logs (log_time, request, response) VALUES (:time, :req, :resp)"
                ),
                [
                    {
                        "time": datetime.now(timezone.utc).isoformat(),
                        "req": dumped_req,
                        "resp": dumped_resp,
                    }
                ],
            )
            con.commit()

        return response


regex_string = None


def enable_funix_host_checker(regex: str):
    global regex_string
    regex_string = regex

    @app.before_request
    def funix_host_check():
        if len(re.findall(regex_string, request.host)) == 0:
            abort(403)
