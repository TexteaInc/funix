class Input:

    def set(self, name, value):
        self.__setattr__(name, value)

    def get(self, name: str):
        return self.__getattribute__(name)


class Output:

    def set(self, value):
        self.value = value

    def get(self):
        return self.value
