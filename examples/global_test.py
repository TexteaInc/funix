from funix import funix


user_word = "https://peps.python.org/pep-0339/"


@funix()
def set_word(word: str) -> str:
    global user_word
    user_word = word
    return "Success"


@funix()
def get_word() -> str:
    return user_word
