from funix import funix_method, funix_class


@funix_class()
class A:
    @funix_method(title="Initialize A", print_to_web=True)
    def __init__(self, a: int):
        self.a = a
        print(f"`self.a` has been initialized to {self.a}")

    def update_a(self, b: int) -> str:
        self.a = b
        return f"`self.a` has been updated to {self.a}"

    def print_a(self) -> str:
        return f"The value of `self.a` is {self.a}"

    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b

    @staticmethod
    @funix_method(title="Returns 1")
    def return_1() -> int:
        return 1
