"""
HTTP File service for funix.
"""

from io import BytesIO
from os.path import abspath, splitext
from uuid import uuid4

from flask import abort, send_file

from funix.app import app
from funix.util.uri import is_valid_uri

__files_dict: dict[str, bytes | str] = {}
"""
A dict, key is file id, value is file content (path or bytes).
"""


def get_real_uri(path_or_file_content: str | bytes) -> str:
    """
    Get the funix relative URI of the file or path.
    For URI, return directly

    Parameters:
        path_or_file_content (str | bytes): The path or file content.

    Returns:
        str: The funix relative URI.

    Raises:
        ValueError: If the path or file content is not valid.
    """
    global __files_dict
    if isinstance(path_or_file_content, bytes):
        fid = uuid4().hex
        result = f"/file/{fid}"
        if path_or_file_content not in list(__files_dict.values()):
            __files_dict[fid] = path_or_file_content
        else:
            return f"/file/{list(__files_dict.keys())[list(__files_dict.values()).index(path_or_file_content)]}"
        return result
    if not is_valid_uri(path_or_file_content):
        fid = uuid4().hex + splitext(path_or_file_content)[1]
        result = f"/file/{fid}"
        abs_path = abspath(path_or_file_content)
        if abs_path not in list(__files_dict.values()):
            __files_dict[fid] = abs_path
        else:
            return f"/file/{list(__files_dict.keys())[list(__files_dict.values()).index(abs_path)]}"
        return result
    else:
        return path_or_file_content


def get_static_uri(path: str | list[str | bytes] | bytes) -> str | list[str]:
    """
    Get the funix relative URI of the file(s), path(s), binary(ies) or uri(s).
    list -> list
    str -> str
    bytes -> str

    Parameters:
        path (str | list[str | bytes] | bytes): The path(s), file(s), binary(ies) or uri(s).

    Returns:
        str | list[str]: The funix relative URI(s).
    """
    if isinstance(path, (str, bytes)):
        return get_real_uri(path)
    elif isinstance(path, list):
        uris = [get_real_uri(uri) for uri in path]
        return uris
    else:
        raise Exception("Unsupported path type")


def enable_file_service():
    @app.get("/file/<string:fid>")
    def __funix_export_file(fid: str):
        """
        Send the file. Funix does not store your file on disk, instead it just stores bytes and str.
        If it is str, then it is treated as path, but if it is bytes, then it is treated as binary.

        Routes:
            /file/<string:fid>: The file path.

        Parameters:
            fid (str): The file id.

        Returns:
            flask.Response: The file.
        """
        if fid in __files_dict:
            if isinstance(__files_dict[fid], str):
                # Like path
                return send_file(__files_dict[fid])
            else:
                # Like binary
                return send_file(
                    BytesIO(__files_dict[fid]), mimetype="application/octet-stream"
                )
        else:
            return abort(404)
