import sys
from typing import Any, Dict, List, Literal, NewType, Optional, Tuple, TypedDict, Text


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
    Dict[Text, Dict[Text, Any]] |
    dict[str, dict[str, Any]]
]


class CodeConfig(TypedDict):
    lang: Optional[str | Text]
    content: Optional[str | Text]


BasicFileType = Optional[List[Text] | Text | list[str] | str]
"""
List[str]:
    For multiple URLs, paths
    For example: ["https://example.org/imgs/1.png", "https://example.org/imgs/2.png"]

str:
    For URL, path
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

_Images = NewType("Images", type(BasicFileType))
Images: TypeAlias = _Images
_Videos = NewType("Videos", type(BasicFileType))
Videos: TypeAlias = _Videos
_Audios = NewType("Audios", type(BasicFileType))
Audios: TypeAlias = _Audios
_Files = NewType("Files", type(BasicFileType))
Files: TypeAlias = _Files

_Code = NewType("Code", type(Optional[str | Text | CodeConfig]))
Code: TypeAlias = _Code
"""
Support Code like:

{
    "lang": "python",
    "content": "print('hello world')"
}

or just a string like "print('hello world')"
frontend will detect the language automatically
"""
