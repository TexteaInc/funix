"""
HTTP File service for funix.
"""

from io import BytesIO
from os.path import abspath, join, splitext
from threading import Timer
from typing import Any
from uuid import uuid4

from flask import Flask, abort, send_file

from funix.config.switch import GlobalSwitchOption
from funix.util.file import create_safe_tempdir
from funix.util.uri import is_valid_uri

__files_dict: dict[str, bytes | str] = {}
"""
A dict, key is file id, value is file content (path or bytes).
"""


def delete_file(fid: str) -> None:
    """
    Delete the file.

    Parameters:
        fid (str): The file id.

    Note:
        Need lock, but it's not a big problem for now I think so?
    """
    global __files_dict
    if fid in __files_dict:
        del __files_dict[fid]


def delete_file_task(fid: str) -> None:
    if GlobalSwitchOption.FILE_LINK_EXPIRE_TIME != -1:
        t = Timer(GlobalSwitchOption.FILE_LINK_EXPIRE_TIME, delete_file, args=(fid,))
        t.start()


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
        new_ref = path_or_file_content
        if GlobalSwitchOption.BIGGER_DATA_SAVE_TO_TEMP != -1:
            if len(path_or_file_content) >= GlobalSwitchOption.BIGGER_DATA_SAVE_TO_TEMP:
                new_ref = join(create_safe_tempdir(), fid)
                with open(new_ref, "wb") as f:
                    f.write(path_or_file_content)
            __files_dict[fid] = new_ref
            delete_file_task(fid)

        if new_ref not in list(__files_dict.values()):
            __files_dict[fid] = new_ref
            delete_file_task(fid)
        else:
            return f"/file/{list(__files_dict.keys())[list(__files_dict.values()).index(new_ref)]}"
        return result
    if not is_valid_uri(path_or_file_content):
        fid = uuid4().hex + splitext(path_or_file_content)[1]
        result = f"/file/{fid}"
        abs_path = abspath(path_or_file_content)
        if abs_path not in list(__files_dict.values()):
            __files_dict[fid] = abs_path
            delete_file_task(fid)
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
    if isinstance(path, str):
        if path.startswith("/file/"):
            return path
        else:
            return get_real_uri(path)
    if isinstance(path, bytes):
        return get_real_uri(path)
    elif isinstance(path, list):
        uris = [get_real_uri(uri) for uri in path]
        return uris
    else:
        raise Exception("Unsupported path type")


def enable_file_service(flask_app: Flask):
    @flask_app.get("/file/<string:fid>")
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


def handle_ipython_audio_image_video(obj: Any) -> str:
    """
    Handle IPython audio, image and video.

    Parameters:
        obj (Any): The object.

    Returns:
        str: The funix relative URI.

    Raises:
        RuntimeError: If the data, url, filename is not found.
        RuntimeError: If the data type is not supported.
    """
    class_ = getattr(obj, "__class__")
    full_name = f"{class_.__module__}.{class_.__name__}"
    if full_name in [
        "IPython.core.display.Audio",
        "IPython.lib.display.Audio",
        "IPython.core.display.Image",
        "IPython.lib.display.Audio",
        "IPython.core.display.Video",
        "IPython.lib.display.Video",
    ]:
        # data, url, filename
        if hasattr(obj, "data") and obj.data is not None:
            if full_name in [
                "IPython.core.display.Audio",
                "IPython.lib.display.Audio",
            ]:
                data_class = getattr(obj.data, "__class__")
                if f"{data_class.__module__}.{data_class.__name__}" == "numpy.ndarray":
                    return get_static_uri(obj.data.tobytes())
                elif isinstance(obj.data, (str, bytes)):
                    return get_static_uri(obj.data)
                elif isinstance(obj.data, list):
                    return get_static_uri(bytes(obj.data))
                else:
                    raise RuntimeError("Unsupported data type in Audio")
            else:
                return get_static_uri(obj.data)
        elif hasattr(obj, "url") and obj.url is not None:
            return get_static_uri(obj.url)
        elif hasattr(obj, "filename") and obj.filename is not None:
            return get_static_uri(obj.filename)
        else:
            raise RuntimeError("No data, url, filename found!")
    else:
        raise RuntimeError("Unsupported type")


def get_file_info(file_id: str) -> str:
    if file_id in __files_dict:
        result = __files_dict[file_id]
        if isinstance(result, str):
            return result
        else:
            size = len(result)
            if size > 16:
                first_16_bytes = result[:16].hex()
            else:
                first_16_bytes = result.hex()
            return f"Binary, Size: {size}, First bytes: {first_16_bytes}"
    else:
        return "Not found"
