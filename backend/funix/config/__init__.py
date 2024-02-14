"""
Shared config.
"""

supported_basic_types_dict = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean",
}
"""
A dict, key is the basic type name, value is the type name in frontend (and for yodas right?).
"""

supported_basic_types = list(supported_basic_types_dict.keys())
"""
A list, contains the basic type names.
"""

supported_basic_file_types = ["Images", "Videos", "Audios", "Files"]
"""
A list, contains the basic file type names.
"""

supported_upload_widgets = ["image", "video", "audio", "file"]
"""
A list, contains the upload widget names.
"""

banned_function_name_and_path = ["list", "file", "static", "config", "param", "call"]
"""
The banned function name and path.

Reason: Funix has used these paths.
"""

basic_widgets = [
    "slider",
    "input",
    "textField",
    "switch",
    "button",
    "checkbox",
    "radio",
]
"""
Basic widgets for MUI components.
"""

builtin_widgets = {
    "Literal": "radio",
}
"""
A dict, key is the type name, value is the MUI component name.

This is the funix builtin widgets.
"""

ipython_type_convert_dict = {
    "IPython.core.display.Markdown": "Markdown",
    "IPython.lib.display.Markdown": "Markdown",
    "IPython.core.display.HTML": "HTML",
    "IPython.lib.display.HTML": "HTML",
    "IPython.core.display.Javascript": "HTML",
    "IPython.lib.display.Javascript": "HTML",
    "IPython.core.display.Image": "Images",
    "IPython.lib.display.Image": "Images",
    "IPython.core.display.Audio": "Audios",
    "IPython.lib.display.Audio": "Audios",
    "IPython.core.display.Video": "Videos",
    "IPython.lib.display.Video": "Videos",
}
"""
A dict, key is the IPython type name, value is the Funix type name.
"""

dataframe_convert_dict = {
    "pandera.typing.pandas.DataFrame": "Dataframe",
    "pandas.core.frame.DataFrame": "Dataframe",
}
"""
A dict, key is the dataframe type name, value is the Funix type name.
"""
