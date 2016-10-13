class Spy:
    def __init__(self):
        self.has_been_called = False

    def to_call(self, *kwargs):
        self.has_been_called = True

    def is_called(self):
        return self.has_been_called
