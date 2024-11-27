import os

class Status:
    def __init__(self):
        self._retries = 0
        self._maxRetries = int(os.getenv('RETRIES'))
        
    def __repr__(self):
        return f'retries:{self._retries} / {self._maxRetries}'
        
    def expired(self):
        return self._retries >= self._maxRetries
    
    def update(self):
        self._retries += 1

    def reset(self):
        self._retries = 0

