from funix import funix


@funix()
def set_word(word: str) -> str:
    global user_word
    user_word = word
    return "Success"


@funix()
def get_word() -> str:
    return user_word
