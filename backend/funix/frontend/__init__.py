import os
from funix.app import app
from flask import send_from_directory

folder = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../build"))


def start():
    @app.route("/")
    def send_index():
        return send_from_directory(folder, "index.html")

    @app.route("/<path:path>")
    def send_static(path):
        if os.path.exists(os.path.join(folder, path)):
            return send_from_directory(folder, path)
        return send_from_directory(folder, "index.html")

    @app.route("/static/css/<path:path>")
    def send_css_static(path):
        return send_from_directory(os.path.abspath(os.path.join(folder, "static/css/")), path)

    @app.route("/static/js/<path:path>")
    def send_js_static(path):
        return send_from_directory(os.path.abspath(os.path.join(folder, "static/js/")), path)

    @app.route("/static/media/<path:path>")
    def send_media_static(path):
        return send_from_directory(os.path.abspath(os.path.join(folder, "static/media/")), path)
