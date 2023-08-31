from funix import funix
from funix.hint import Markdown, StrCode, StrTextarea


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
def theme_test_mood(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(title="Pink", theme="./pink.json")
def theme_test_pink(markdown: StrCode("markdown")) -> Markdown:
    return markdown


@funix(
    title="Pirated Funix",
    description="Oops, you're using a pirated version of Funix and we're upset. Your page will use Comic Sans MS as "
    "the display font (haha, that is a joke)",
    theme="./comic_sans.json",
    argument_labels={"license_key": "License Key"},
)
def pirated_funix(license_key: str | None = None) -> Markdown:
    return (
        "Invalid activation code, please go to [official website](https://github.com/TexteaInc/funix) for more "
        "information"
    )
