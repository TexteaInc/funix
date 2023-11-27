from funix import funix_method, funix_class


@funix_class()
class A:
    @funix_method(title="Initialize A")
    def __init__(self, a: int):
        self.a = a

    @funix_method(title="a = b + c")
    def abc(self, b: int, c: int) -> None:
        self.a = b + c

    @funix_method(title="Returns a")
    def b(self) -> int:
        return self.a

    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b

    @staticmethod
    @funix_method(title="Returns 1")
    def return_1() -> int:
        return 1
