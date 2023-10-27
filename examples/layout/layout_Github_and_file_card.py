import funix 
from funix.hint import File
import IPython

# layout
@funix.funix(
    title="Layout and File downloader card",
    description="This example create a card for a Github repo based on the user name and repo name. The purpose of this example is to show how to customize the layout in a row-based grid approach.",
    # argument_labels={
    #   "user_name": "username",
    # },
    input_layout=[
        [
            {"html": "https://github.com/", "width": 3.5},
            {"argument": "user_name", "width": 4},
            {"html": "/", "width": 0.2},
            {"argument": "repo_name", "width": 4},
        ]
        # all in row 1
    ],
    output_layout=[
        [{"return_index": 0}],  # row 1
        [{"markdown": "**Download Link**", "width": 2}, {"return_index": 1}],  # row 2
        [{"markdown": "**Visit the repo**"}, {"return_index": 2}],  # row 3
    ],
    show_source=True,
)
def layout_example(
    user_name: str = "texteainc", repo_name: str = "funix"
) -> (IPython.display.Image, File, IPython.display.Markdown):
    url = f"https://github.com/{user_name}/{repo_name}"
    author = url.split("/")[3]
    name = url.split("/")[4]
    return (
        f"https://opengraph.githubassets.com/1/{author}/{name}",
        f"{url}/archive/refs/heads/main.zip",
        f"[{url}]({url})",
    )
