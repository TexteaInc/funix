
import typing 

import funix 

used_letters = []
secret_word = "funix"

@funix.funix(
    argument_labels={
        "letter": "Enter a letter"
    }
)

def guess_letter(letter: str) -> \
    (funix.hint.Markdown, str,   # type hint here
    funix.hint.HTML, 
    funix.hint.Markdown, str):   
    global used_letters # state/session as global
    used_letters.append(letter)
    answer = "".join([
        (letter if letter in used_letters else "_")
            for letter in secret_word
        ])

    return "### Hangman", answer, \
           "<hr>", \
           "### Used letters", f"[{', '.join(used_letters)}]"

