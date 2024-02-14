"""
Websocket class to redirect
"""

from io import StringIO
from json import dumps


class StdoutToWebsocket:
    """
    Stdout to websocket.
    """

    def __init__(self, ws):
        """
        Initialize the StdoutToWebsocket.

        Parameters:
            ws (WebSocket): The websocket.
        """
        self.ws = ws
        self.value = StringIO()

    def write(self, data):
        """
        Write the data to the websocket.
        """
        self.value.write(data)
        self.ws.send(dumps([self.value.getvalue()]))

    def writelines(self, data):
        """
        Write the lines to the websocket.
        """
        self.value.writelines(data)
        self.ws.send(dumps([self.value.getvalue()]))

    def flush(self):
        """
        Flush the data to the websocket.
        """
        self.value.flush()
        self.ws.send(dumps([self.value.getvalue()]))
        self.value = StringIO()
