from funix import import_theme, funix
from funix.hint import Markdown, StrCode


import_theme(alias="oops", path="themes/dark_test.py", dict_name="theme")


description = """
This a markdown playground. You can write markdown here and see the result on the right side.
And with a test dark mode theme.

You can get this demo and theme file in funix examples
"""


@funix(
    title="Theme Test & Markdown Playground",
    description=description,
    theme_name="oops"
)
def theme_test_markdown_playground(markdown: StrCode("markdown")) -> Markdown:
    return markdown
