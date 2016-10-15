class Spy:
    def __init__(self):
        self._has_been_called = False

    def to_call(self, *kwargs):
        self._has_been_called = True

    def is_called(self):
        return self._has_been_called
