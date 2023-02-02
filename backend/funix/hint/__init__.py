from typing import Any, Dict, List, Literal, Optional, Tuple, NewType, TypedDict

# See Document in Notion
DestinationType = Literal["column", "row", "sheet", None]
WidgetsType = Optional[Dict[Tuple | str, List[str] | str]]
TreatAsType = Optional[Dict[Tuple | str, str]]
WhitelistType = Optional[Dict[Tuple | str, List[Any] | List[List[Any]]]]
ExamplesType = Optional[Dict[Tuple | str, List[Any] | List[List[Any]]]]
LabelsType = Optional[Dict[Tuple | str, str]]
LayoutType = Optional[List[List[Dict[str, str]]]]
ConditionalVisibleType = Optional[List[Dict[str, List[str] | Dict[str, Any]]]]
ArgumentConfigType = Optional[Dict[str, Dict[str, Any]]]


class CodeConfig(TypedDict):
    lang: str
    content: str


BasicFileType = Optional[List[str] | str]
"""
List[str]:
    For multiple URLs, paths
    For example: ["https://example.org/imgs/1.png", "https://example.org/imgs/2.png"]

str:
    For URL, path
    For example: "https://example.org/imgs/1.png"
"""

Markdown = NewType("Markdown", Optional[str])
"""
Support Markdown like "**bold**" and "*italic*"
"""

HTML = NewType("HTML", Optional[str])
"""
Support HTML like "<span style='color: red'>red</span>"
"""

Images = NewType("Images", BasicFileType)
Videos = NewType("Videos", BasicFileType)
Audios = NewType("Audios", BasicFileType)
Files = NewType("Files", BasicFileType)

Code = NewType("Code", Optional[CodeConfig | str])
"""
Support Code like:

{
    "lang": "python",
    "content": "print('hello world')"
}

or just a string like "print('hello world')"
frontend will detect the language automatically
"""
