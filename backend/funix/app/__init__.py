"""
Save the app instance here
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from flask import Flask, Response, abort, request
from flask_sock import Sock
from sqlalchemy import create_engine, text
from sqlalchemy.pool import SingletonThreadPool

from funix.config.switch import GlobalSwitchOption
from funix.decorator.file import get_file_info
from funix.decorator.lists import get_uuid_with_name
from funix.frontend import start
from funix.hint import LogLevel

from json import loads

app = Flask(__name__)
app.secret_key = GlobalSwitchOption.get_session_key()
app.config.update(
    SESSION_COOKIE_PATH="/",
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_TYPE="filesystem",
)
app.json.sort_keys = False
sock = Sock(app)

matplotlib_figure_manager = {}


class MatplotlibWebsocket:
    supports_binary = True

    def __init__(self, manager=None, ws=None):
        self.manager = manager
        self.ws = ws
        if self.manager is not None:
            self.manager.add_web_socket(self)
        self.supports_binary = True

    def on_close(self):
        self.manager.remove_web_socket(self)
        self.ws.close()

    def set_manager(self, manager):
        self.manager = manager
        self.manager.add_web_socket(self)

    def set_ws(self, ws):
        self.ws = ws

    def on_message(self, message: dict):
        if message["type"] == "supports_binary":
            self.supports_binary = message["value"]
        else:
            self.manager.handle_json(message)

    def send_json(self, content: dict):
        self.ws.send(json.dumps(content))

    def send_binary(self, content: bytes):
        if self.supports_binary:
            self.ws.send(content)
        else:
            data_uri = "data:image/png;base64," + content.decode("utf-8")
            self.ws.send(data_uri)


matplotlib_figure_managers = {}


def add_sock_route(flask_sock: Sock):
    @flask_sock.route("/ws-plot/<path:figure_id>")
    def __ws_plot(ws, figure_id: str):
        """
        WebSocket route for plot.

        Routes:
            /ws-plot: The WebSocket route for plot.

        Parameters:
            ws (Any): The WebSocket.

        Returns:
            None
        """
        if figure_id not in matplotlib_figure_managers:
            manager_class = MatplotlibWebsocket(
                matplotlib_figure_manager[int(figure_id)], ws
            )
            matplotlib_figure_managers[int(figure_id)] = manager_class
        else:
            manager_class = matplotlib_figure_managers[int(figure_id)]
            manager_class.set_ws(ws)
        while True:
            data = ws.receive()
            if data is not None:
                dict_data = loads(data)
                manager_class.on_message(dict_data)


def add_app_route(flask_app: Flask):
    @flask_app.route("/plot-download/<path:figure_id>/<path:format>")
    def __ws_plot(figure_id: str, format: str):
        """
        Download the plot.

        Routes:
            /plot-download: The route to download the plot.

        Parameters:
            figure_id (str): The figure id.
            format (str): The format of the plot.

        Returns:
            None
        """
        buffer = BytesIO()
        manager = matplotlib_figure_manager[int(figure_id)]
        manager.canvas.figure.savefig(buffer, format=format)
        buffer.seek(0)
        buffer_name = f"plot.{format}"
        return Response(
            buffer,
            mimetype="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={buffer_name}",
                "Content-Length": str(len(buffer.getvalue())),
            },
        )


add_sock_route(sock)


def funix_auto_cors(response: Response) -> Response:
    if "HTTP_ORIGIN" not in request.environ:
        response.headers["Access-Control-Allow-Origin"] = "*"
    else:
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Origin"] = request.environ["HTTP_ORIGIN"]
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, *"

    return response


def get_new_app_and_sock_for_jupyter() -> tuple[Flask, Sock]:
    """
    Get a new Flask app and a new Sock instance.
    No telemetry, logging and visitor checks (fixed to 127.0.0.1)

    Returns:
        tuple[Flask, Sock]: The new Flask app and the new Sock instance.
    """
    new_app = Flask(f"Junix_{uuid4().hex}")
    new_app.secret_key = "Jupiter"
    new_app.config.update(
        SESSION_COOKIE_PATH="/",
        SESSION_COOKIE_SAMESITE="None",
        SESSION_TYPE="filesystem",
    )
    new_sock = Sock(new_app)
    add_sock_route(new_sock)
    new_app.after_request(funix_auto_cors)
    start(new_app)

    return new_app, new_sock


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


app.after_request(funix_auto_cors)


def get_real_ip() -> str:
    # I don't think this is a good way for all reverse proxies
    # ip = request.remote_addr
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    return request.remote_addr


def __api_call_data(
    app_name: str, response: Response, dict_to_json: bool = False
) -> dict | None:
    if funix_log_level == LogLevel.OFF:
        return

    if (
        funix_log_level == LogLevel.OPTIONAL
        and request.cookies.get("DO_NOT_LOG_ME") == "YES"
    ):
        return

    try:
        req_json = request.json
    except:
        req_json = None

    try:
        resp_json = response.json
    except:
        resp_json = None

    url = request.url
    path = urlparse(url).path

    dumped_req = {
        "ip": get_real_ip(),
        "url": url,
        "headers": dict(request.headers),
        "data": req_json,
    }

    if path.startswith(("/call/", "/param/", "/verify/", "/update/")):
        result = path.split("/")
        if len(result) < 3:
            return
        id_ = "/".join(result[2:])
        dumped_req["function"] = get_uuid_with_name(app_name, id_)

    if path.startswith("/file/"):
        result = path.split("/")
        if len(result) < 3:
            return
        id_ = result[-1]
        dumped_req["file"] = get_file_info(id_)

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

            data = __api_call_data(app.name, response, dict_to_json=True)
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

            data = __api_call_data(app.name, response)
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
