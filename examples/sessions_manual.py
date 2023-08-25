from funix import funix
from funix.session import get_global_variable, set_global_variable, set_default_global_variable


set_default_global_variable("user_word", "https://peps.python.org/pep-0339/")


@funix()
def set_word(word: str) -> str:
    set_global_variable("user_word", word)
    return "Success"


@funix()
def get_word() -> str:
    return get_global_variable("user_word")
