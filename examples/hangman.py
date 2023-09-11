# The hangman game with funix

import funix
from IPython.display import Markdown

secret_word = "funix"
used_letters = []


@funix.funix(argument_labels={"letter": "Enter letter"})
def guess_letter(letter: str) -> Markdown:
    global used_letters  # state/session as global
    used_letters.append(letter)
    answer = "".join(
        [(letter if letter in used_letters else "_") for letter in secret_word]
    )
    return Markdown(
        data=f"### Hangman \n `{answer}` \n\n ---- \n ### Used letters \n {', '.join(used_letters)}"
    )
