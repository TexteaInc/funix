from typing import Any, Dict, List, Literal, NewType, Optional, Tuple, TypedDict, Text, TypeAlias
from ..widget import builtin


DestinationType = Literal["column", "row", "sheet", None]
WidgetsType = Optional[
    Dict[Tuple | Text, List[Text] | Text] |
    dict[tuple | str, list[str] | str]
]
TreatAsType = Optional[
    Dict[Tuple | Text, Text] |
    dict[tuple | str, str]
]
WhitelistType = Optional[
    Dict[Tuple | Text, List[Any] | List[List[Any]]] |
    dict[tuple | str, list | list[list]]
]
ExamplesType = Optional[
    Dict[Tuple | Text, List[Any] | List[List[Any]]] |
    dict[tuple | str, list | list[list]]
]
LabelsType = Optional[
    Dict[Tuple | Text, Text] |
    dict[tuple | str, str]
]
LayoutType = Optional[
    List[List[Dict[Text, Any]]] |
    list[list[dict[str, Any]]]
]
ConditionalVisibleType = Optional[
    List[Dict[Text, List[Text] | Dict[Text, Any]]] |
    list[dict[str, list[str] | dict[str, Any]]]
]
ArgumentConfigType = Optional[
    Dict[Text | Tuple, Dict[Text, Any]] |
    dict[str | tuple, dict[str, Any]]
]


class CodeConfig(TypedDict):
    lang: Optional[str | Text]
    code: Optional[str | Text]


BasicFileType = Optional[Text | str | bytes]
"""
For URL, path, bytes
For example: "https://example.org/imgs/1.png"
"""

_Markdown = NewType("Markdown", type(Optional[str | Text]))
Markdown: TypeAlias = _Markdown
"""
Support Markdown like "**bold**" and "*italic*"
"""

_HTML = NewType("HTML", type(Optional[str | Text]))
HTML: TypeAlias = _HTML
"""
Support HTML like "<span style='color: red'>red</span>"
"""

_Image = NewType("Images", type(BasicFileType))
Image: TypeAlias = _Image
_Video = NewType("Videos", type(BasicFileType))
Video: TypeAlias = _Video
_Audio = NewType("Audios", type(BasicFileType))
Audio: TypeAlias = _Audio
_File = NewType("Files", type(BasicFileType))
File: TypeAlias = _File

_Code = NewType("Code", type(Optional[str | Text | CodeConfig]))
Code: TypeAlias = _Code
"""
Support Code like:

{
    "lang": "python",
    "code": "print('hello world')"
}

or just a string like "print('hello world')"
"""

IntInputBox: TypeAlias = builtin.IntInputBox
IntSlider = builtin.IntSlider
FloatInputBox: TypeAlias = builtin.FloatInputBox
FloatSlider = builtin.FloatSlider
StrCode = builtin.StrCode
StrInputBox: TypeAlias = builtin.StrInputBox
StrTextarea: TypeAlias = builtin.StrTextarea
StrPassword: TypeAlias = builtin.StrPassword
BoolCheckBox: TypeAlias = builtin.BoolCheckBox
BoolSwitch: TypeAlias = builtin.BoolSwitch
BytesImage: TypeAlias = builtin.BytesImage
BytesVideo: TypeAlias = builtin.BytesVideo
BytesAudio: TypeAlias = builtin.BytesAudio
BytesFile: TypeAlias = builtin.BytesFile
