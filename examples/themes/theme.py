from funix import funix
from funix.hint import Markdown, StrCode


description = """
This a markdown playground. You can write markdown here and see the result on the right side.
And with a test dark mode theme.

You can get this demo and theme file in funix examples
"""


@funix(
    title="Markdown Playground",
    description=description,
    theme="./dark_test.json",
)
def theme_test_markdown_playground(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(
    title="Mood",
    description="But in sunset",
    theme="./sunset.json",
)
def theme_test_mood(markdown: StrCode("markdown"), a: int) -> Markdown:
    return markdown
