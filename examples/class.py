from funix import funix_method, funix_class
from IPython.display import Markdown

@funix_class()
class A:
    @funix_method(title="Initialize A", print_to_web=True)
    def __init__(self, a: int):
        self.a = a
        print(f"`self.a` has been initialized to {self.a}")

    def set(self, b: int) -> Markdown:
        self.a = b
        return f"`self.a` has been updated to {self.a}"

    def get(self) -> Markdown:
        return f"The value of `self.a` is {self.a}"

    @staticmethod
    @funix_method(disable=True)
    def add(a: int, b: int) -> int:
        return a + b

    @staticmethod
    @funix_method(title="Returns 1", disable=True)
    def return_1() -> int:
        return 1
