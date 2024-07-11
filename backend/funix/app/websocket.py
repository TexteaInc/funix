"""
Websocket class to redirect
"""
from io import StringIO
from json import dumps


class StdoutToWebsocket:
    """
    Stdout to websocket.
    """

    encoding = "utf-8"

    def __init__(self, ws, is_err=False):
        """
        Initialize the StdoutToWebsocket.

        Parameters:
            ws (WebSocket): The websocket.
        """
        self.ws = ws
        self.is_err = is_err
        self.value = StringIO()

    def _get_html(self):
        """
        Get the html data.
        """
        value = self.value.getvalue()
        if self.is_err and value.strip():
            return f"`{value}`"
        return value

    def write(self, data):
        """
        Write the data to the websocket.
        """
        self.value.write(data)
        self.ws.send(dumps([self._get_html()]))

    def writelines(self, data):
        """
        Write the lines to the websocket.
        """
        self.value.writelines(data)
        self.ws.send(dumps([self._get_html()]))

    def flush(self):
        """
        Flush the data to the websocket.
        """
        self.value.flush()
        self.ws.send(dumps([self._get_html()]))
        self.value = StringIO()
