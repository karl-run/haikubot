class Spy:
    def __init__(self):
        self._has_been_called = False
        self.args = {}
        self.times_called = 0

    def to_call(self, *kwargs):
        self._has_been_called = True
        self.args = kwargs
        self.times_called += 1

    def is_called(self):
        return self._has_been_called

    def is_called_times(self, num):
        return self.times_called == num