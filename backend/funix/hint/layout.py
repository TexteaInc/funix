"""
Layout components for hint
"""

from typing import Literal, Optional, TypedDict

Number = int | float


class LayoutComponentMarkdown(TypedDict):
    """
    Markdown component
    """

    markdown: str
    """
    Markdown text
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentHTML(TypedDict):
    """
    HTML component
    """

    html: str
    """
    HTML text
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentDivider(TypedDict):
    """
    Divider component
    """

    divider: bool | str
    """
    Divider
    
    When type is str, it will render divider with text, or it will render a normal divider
    """

    position: Optional[Literal["left", "center", "right"]]
    """
    Optional position, default is `center`
    
    Only works when divider is str
    """


class LayoutComponentArgument(TypedDict):
    """
    Input component
    """

    argument: str
    """
    Argument name
    
    Function argument name
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentReturn(TypedDict):
    """
    Output component
    """

    return_index: int | list[int]
    """
    Return index
    
    Function return index
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentImages(TypedDict):
    """
    Images component
    """

    images: list[str] | str
    """
    Images
    
    URL or path should be provided
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentVideos(TypedDict):
    """
    Videos component
    """

    videos: list[str] | str
    """
    Videos

    URL or path should be provided
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentAudios(TypedDict):
    """
    Audios component
    """

    Audios: list[str] | str
    """
    Audios

    URL or path should be provided
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentFiles(TypedDict):
    """
    Files component
    """

    files: list[str] | str
    """
    Files

    URL or path should be provided
    """

    width: Optional[Number]
    """
    Optional width, max is 12.0
    """


class LayoutComponentCode(TypedDict):
    """
    Code component
    """

    code: str
    """
    Code text
    """

    lang: Optional[str]
    """
    Optional language, frontend will highlight code with this language
    
    Default is `plaintext`
    """


CommonLayoutComponents = (
    LayoutComponentMarkdown
    | LayoutComponentHTML
    | LayoutComponentDivider
    | LayoutComponentCode
)
"""
Common layout components

Common layout components are components that can be used in both input and output
"""

InputLayoutComponents = CommonLayoutComponents | LayoutComponentArgument
"""
Input layout components

Input layout components are components that can be used in input
"""

OutputLayoutComponents = (
    CommonLayoutComponents
    | LayoutComponentReturn
    | LayoutComponentImages
    | LayoutComponentVideos
    | LayoutComponentAudios
    | LayoutComponentFiles
)
"""
Output layout components

Output layout components are components that can be used in output
"""

AllLayoutComponents = (
    CommonLayoutComponents | InputLayoutComponents | OutputLayoutComponents
)
"""
All layout components

All layout components are components that can be used in both input and output
"""


InputRow = list[InputLayoutComponents]
"""
Input Row

Examples:
    [{"markdown": "Hello world!"}, {"argument": "a"}]
"""

OutputRow = list[OutputLayoutComponents]
"""
Output Row

Examples:
    [{"markdown": "Hello world!"}, {"return": 0}]
"""
