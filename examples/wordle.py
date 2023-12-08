import random
import string
from funix import funix_class, funix_method
from funix.hint import HTML

import json


with open("./files/words.json", "r") as f:
    words = json.load(f)


def random_5_letter() -> str:
    """
    Get random 5 letter
    """
    return "".join(random.choices(string.ascii_lowercase, k=5))


@funix_class()
class Wordle:
    @funix_method(
        title="Wordle Settings",
        description="Settings for the Wordle",
        argument_labels={
            "random_word": "Random 5-letter"
        }
    )
    def __init__(self, random_word: bool = False):
        self.random_word = random_word

        self.word = random_5_letter() if random_word else random.choice(words)
        self.history = []

        self.mismatch = False

        print(self.word)

    def __reset(self):
        self.word = random_5_letter() if self.random_word else random.choice(words)
        self.history = []

    def __push(self, word: str):
        if len(word) != 5 or not word.isalpha():
            self.mismatch = True
        else:
            self.mismatch = False
            if len(self.history) > 6:
                self.__reset()
            self.history.append(word.lower())

    def __generate(self) -> HTML:
        html_code = ""
        for i in range(6):
            html_code += f"<div id='line-{i+1}' style='width: 548px; display: flex; flex-wrap: wrap; justify-content: space-around; {'margin-top: 12px' if i > 0 else ''}'>"
            if i < len(self.history):
                for single_word_index in range(5):
                    single_word = self.history[i][single_word_index]
                    single_word_color = "rgb(156, 163, 175)"
                    if single_word in self.word:
                        single_word_color = "rgb(251, 191, 36)"
                        if single_word == self.word[single_word_index]:
                            single_word_color = "rgb(34, 197, 94)"
                    html_code += f"<div id='line-{i+1}-{single_word_index+1}' style='width: 100px; height: 100px; background-color: {single_word_color}; display: flex; justify-content: center; color: #fff; line-height: 1; font-size: 60px; font-weight: 700; align-items: center;'>{single_word}</div>"
            else:
                for j in range(5):
                    html_code += f"<div id='line-{i+1}-{j+1}' style='width: 100px; height: 100px; background-color: rgb(147, 197, 253); display: flex; justify-content: center; color: #fff; line-height: 1; font-size: 60px; font-weight: 700; align-items: center;'></div>"
            html_code += "</div>"
        if self.mismatch:
            html_code += "<span>Word mismatch, please enter a 5-letter word</span>"
        if len(self.history) > 0 and self.history[-1] == self.word:
            self.__reset()
            html_code += "<span>Game Over, you win!</span>"
        elif len(self.history) == 6:
            html_code += f"<span>Game Over, answer is: <strong>{self.word}</strong></span>"
        return html_code

    def guess(self, word: str) -> HTML:
        self.__push(word)
        return self.__generate()
