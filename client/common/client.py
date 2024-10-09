class Client:
    def __init__(self):
        self._working = True

    def stop(self, _signum, _frame):
        self._working = False