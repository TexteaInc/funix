from funix import funix_class


class A:
    def __init__(self, a: int):
        self.a = a

    def abc(self, b: int, c: int) -> None:
        self.a = b + c

    def b(self) -> int:
        return self.a

    @staticmethod
    def e(a: int, b: int) -> int:
        return a + b

    @staticmethod
    def c() -> int:
        return 1


funix_class(A)
