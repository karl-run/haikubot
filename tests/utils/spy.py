class Spy:
    def __init__(self):
        self._has_been_called = False
        self.args = {}

    def to_call(self, *kwargs):
        self._has_been_called = True
        self.args = kwargs

    def is_called(self):
        return self._has_been_called
