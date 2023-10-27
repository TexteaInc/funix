from funix import funix
from funix.hint import Markdown, StrCode, StrTextarea


description = """
This a markdown playground in the {theme} mode theme. You can write markdown here and see the result on the right.
"""

@funix(
    title="Dark",
    description=description.format(theme="dark"),
    theme="./dark_test.json",
    show_source=True
)
def theme_test_markdown_playground(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(
    title="Sunset",
    description=description.format(theme="sunset"),
    theme="./sunset.json",
    show_source=True
)
def theme_sunset(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(
    title="Pink", 
    description=description.format(theme="pink"), 
    theme="./pink.json",
    show_source=True
    )
def theme_test_pink(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(
    title="Comic Sans",
    description=description.format(theme="Comic Sans"),
    theme="./comic_sans.json",
    show_source=True
)
def theme_comic_sans(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(
    title="Kanagawa",
    description=description.format(theme="Kanagawa"),
    theme="./kanagawa.json",
    show_source=True
)
def theme_kanagawa(markdown: StrCode("markdown")) -> Markdown:
    return markdown