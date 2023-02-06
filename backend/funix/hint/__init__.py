from typing import Any, Dict, List, Literal, Optional, Tuple, NewType, TypedDict, Text

# See Document in Notion
DestinationType = Literal["column", "row", "sheet", None]
WidgetsType = Optional[Dict[Tuple or Text, List[Text] or Text]]
TreatAsType = Optional[Dict[Tuple or Text, Text]]
WhitelistType = Optional[Dict[Tuple or Text, List[Any] or List[List[Any]]]]
ExamplesType = Optional[Dict[Tuple or Text, List[Any] or List[List[Any]]]]
LabelsType = Optional[Dict[Tuple or Text, Text]]
LayoutType = Optional[List[List[Dict[Text, Text]]]]
ConditionalVisibleType = Optional[List[Dict[Text, List[Text] or Dict[Text, Any]]]]
ArgumentConfigType = Optional[Dict[Text, Dict[Text, Any]]]


class CodeConfig(TypedDict):
    lang: str
    content: str


BasicFileType = Optional[List[Text] or Text]
"""
List[str]:
    For multiple URLs, paths
    For example: ["https://example.org/imgs/1.png", "https://example.org/imgs/2.png"]

str:
    For URL, path
    For example: "https://example.org/imgs/1.png"
"""

Markdown = NewType("Markdown", Optional[Text])
"""
Support Markdown like "**bold**" and "*italic*"
"""

HTML = NewType("HTML", Optional[Text])
"""
Support HTML like "<span style='color: red'>red</span>"
"""

Images = NewType("Images", BasicFileType)
Videos = NewType("Videos", BasicFileType)
Audios = NewType("Audios", BasicFileType)
Files = NewType("Files", BasicFileType)

Code = NewType("Code", Optional[CodeConfig or Text])
"""
Support Code like:

{
    "lang": "python",
    "content": "print('hello world')"
}

or just a string like "print('hello world')"
frontend will detect the language automatically
"""
