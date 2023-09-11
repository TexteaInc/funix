# The hangman game with funix

import funix
from IPython.display import Markdown

secret_word = "funix"
used_letters = [] # a global variable 
                  # to maintain the state/session






@funix.funix(
    # argument_labels={
    #     "letter": "Enter letter"
    # }
)
def guess_letter(enter_letter: str) -> IPython.display.Markdown:
    letter = enter_letter # rename
    global used_letters # state/session as global
    used_letters.append(letter)
    answer = "".join([
        (letter if letter in used_letters else "_")
            for letter in secret_word
        ])
    return f"### Hangman \n `{answer}` \n\n ---- \n ### Used letters \n {', '.join(used_letters)}"
