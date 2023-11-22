from funix import funix_class, funix_class_params


class A:
    def __init__(self):
        self.a = 1

    @funix_class_params(title="okay")
    def abc(self, b: int, c: int) -> None:
        self.a = b + c

    def b(self) -> int:
        return self.a


funix_class(A())
