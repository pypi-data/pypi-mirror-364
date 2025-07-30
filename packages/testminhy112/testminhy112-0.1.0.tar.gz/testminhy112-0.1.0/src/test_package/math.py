class MyMath:
    def __init__(self, value:int) -> None:
        self.value = value
    def factorial(self) -> int:
        if self.value == 0:
            return 1
        return self.value * self.factorial(self.value - 1)
    