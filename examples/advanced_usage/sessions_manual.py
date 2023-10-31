from funix import funix
from funix.session import get_global_variable, set_global_variable, set_default_global_variable


set_default_global_variable("user_word", "Funix.io rocks! ")


@funix()
def set_word(word: str) -> str:
    set_global_variable("user_word", word)
    return "Success"


@funix()
def get_word() -> str:
    return get_global_variable("user_word")
