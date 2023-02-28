import os
import json
from funix.app import app
from flask import send_from_directory

folder = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../build"))

@app.route("/")
def send_index():
    return send_from_directory(folder, "index.html")

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory(folder, path)

@app.route("/static/css/<path:path>")
def send_css_static(path):
    return send_from_directory(os.path.abspath(os.path.join(folder, "static/css/")), path)

@app.route("/static/js/<path:path>")
def send_js_static(path):
    return send_from_directory(os.path.abspath(os.path.join(folder, "static/js/")), path)

def start(host: str, port: int):
    @app.route("/config/backend")
    def send_backend_config():
        return json.dumps({"backend": f"http://{host}:{port}"})
