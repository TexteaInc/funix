import typing 
import IPython

# HTML and Markdown outputs 
def html_and_markdown() -> \
    typing.Tuple[IPython.display.HTML, IPython.display.Markdown]:
    return IPython.display.HTML("<p><a href='http://funix.io'>Funix rocks!</a></p>"), \
        IPython.display.Markdown("## Funix rocks!")