from funix import funix
from funix.widget.buildin import StrCode
from funix.hint import Code


@funix()
def more_more_input(
    single_code: StrCode("python"),
) -> Code:
    return {
        "lang": "python",
        "code": single_code
    }
