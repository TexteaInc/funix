from funix import funix_class


class A:
    def __init__(self):
        self.a = 1

    def abc(self, b: int, c: int) -> None:
        self.a = b + c

    def b(self) -> int:
        return self.a


funix_class(A())
