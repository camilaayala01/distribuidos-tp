import os

MAX_RETRIES = int(os.getenv('RETRIES'))
class Status:
    def __init__(self):
        self._retries = 0
        
    def __repr__(self):
        return f'retries:{self._retries} / {MAX_RETRIES}'
        
    def expired(self):
        return self._retries >= MAX_RETRIES
    
    def update(self):
        self._retries += 1

    def reset(self):
        self._retries = 0

