from funix import funix


user_word = "https://peps.python.org/pep-0339/"


@funix(
    session_variables=["user_word"],
)
def set_word(word: str) -> str:
    global user_word
    user_word = word
    return "Success"


@funix(
    session_variables=["user_word"],
)
def get_word() -> str:
    return user_word
