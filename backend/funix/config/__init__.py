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
