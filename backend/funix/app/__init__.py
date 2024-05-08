"""
Save the app instance here
"""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, abort, request
from flask_sock import Sock
from sqlalchemy import create_engine, text
from sqlalchemy.pool import SingletonThreadPool

from funix.config.switch import GlobalSwitchOption
from funix.hint import LogLevel

app = Flask(__name__)
app.secret_key = GlobalSwitchOption.get_session_key()
app.config.update(
    SESSION_COOKIE_PATH="/",
    SESSION_COOKIE_SAMESITE="None",
    SESSION_TYPE="filesystem",
)
sock = Sock(app)

funix_log_level = LogLevel.get_level()

privacy = """We honor your choices. For your data and freedom.

1. We do not share your data with third party organizations. 
2. Your IP address, browser header data, access time, access address, cookie data, request and response data will be \
recorded. We will use this data to improve our services and provide better user experience.
3. You can tell Funix that you refuse to collect the above information by clicking on the "Do not track me" button \
below.
4. Clicking "Agree" indicates that you agree to the above data policy.
"""

privacy_update_hash = hashlib.sha256(
    privacy.encode() + str(funix_log_level.value).encode()
).hexdigest()


@app.get("/privacy")
def __funix_privacy():
    return {
        "text": privacy,
        "log_level": int(funix_log_level.value),
        "hash": privacy_update_hash,
    }


def privacy_policy(message: str) -> None:
    """
    Set the privacy policy.

    Parameters:
        message (str): The privacy policy message.

    Returns:
        None
    """
    global privacy, privacy_update_hash
    privacy_update_hash = hashlib.sha256(
        message.encode() + str(funix_log_level.value).encode()
    ).hexdigest()
    privacy = message


@app.after_request
def funix_auto_cors(response: Response) -> Response:
    if "HTTP_ORIGIN" not in request.environ:
        response.headers["Access-Control-Allow-Origin"] = "*"
    else:
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Origin"] = request.environ["HTTP_ORIGIN"]
    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, *"
    
    return response


def __api_call_data(response: Response, dict_to_json: bool = False) -> dict | None:
    do_not_log_me = (
        request.cookies.get("DO_NOT_LOG_ME") and funix_log_level != LogLevel.MANDATORY
    )
    if do_not_log_me is not None and do_not_log_me == "YES":
        return

    try:
        req_json = request.json
    except:
        return

    if req_json is None:
        return

    try:
        resp_json = response.json
    except:
        return

    if resp_json is None:
        return

    dumped_req = {
        "url": request.url,
        "headers": dict(request.headers),
        "data": req_json,
    }

    now = datetime.now(timezone.utc).isoformat()

    if dict_to_json:
        return {
            "time": now,
            "request": json.dumps(dumped_req),
            "response": json.dumps(resp_json),
        }

    return {
        "time": now,
        "request": dumped_req,
        "response": resp_json,
    }


if funix_log_level != LogLevel.OFF:
    storage_path = Path(os.environ.get("FUNIX_TELEMETRY_STORAGE", default="logs.jsonl"))
    if storage_path.suffix == ".db":
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
        def funix_database_logger(response: Response) -> Response:
            global con

            data = __api_call_data(response, dict_to_json=True)
            if data is None:
                return response

            with engine.connect() as con:
                con.execute(
                    text(
                        "INSERT INTO logs (log_time, request, response) VALUES (:time, :request, :response)"
                    ),
                    [data],
                )
                con.commit()

            return response

    elif storage_path.suffix == ".jsonl":
        jsonl_file = open(storage_path, "a", buffering=1)

        @app.after_request
        def funix_database_logger(response: Response) -> Response:
            global jsonl_file

            data = __api_call_data(response)
            if data is None:
                return response

            jsonl_file.write(json.dumps(data))
            jsonl_file.write("\n")

            return response

    else:
        raise ValueError(
            f"The value of `FUNIX_TELEMETRY_STORAGE` is {storage_path}, "
            f"Funix only supports `jsonl` or `db` file."
        )


regex_string = None


def enable_funix_host_checker(regex: str):
    global regex_string
    regex_string = regex

    @app.before_request
    def funix_host_check():
        if len(re.findall(regex_string, request.host)) == 0:
            abort(403)
