import os
import json
from flask import Flask, send_from_directory

folder = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../build"))
frontend_app = Flask("funix.frontend")

@frontend_app.route("/")
def send_index():
    return send_from_directory(folder, "index.html")

@frontend_app.route("/<path:path>")
def send_static(path):
    return send_from_directory(folder, path)

@frontend_app.route("/static/css/<path:path>")
def send_css_static(path):
    return send_from_directory(os.path.abspath(os.path.join(folder, "static/css/")), path)

@frontend_app.route("/static/js/<path:path>")
def send_js_static(path):
    return send_from_directory(os.path.abspath(os.path.join(folder, "static/js/")), path)

def start(host: str, port: int, backend_port: int):
    @frontend_app.route("/config/backend")
    def send_backend_config():
        return json.dumps({"backend": f"http://{host}:{backend_port}"})
    frontend_app.run(host, port)
