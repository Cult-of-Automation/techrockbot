import logging
import time

from tests.variables import _get

class ListenerCooldown(object):
    
    def __init__(self, gid, cooldown):
        self.limit = _get(gid, 'cooldown', cooldown)[0]
        self.duration = _get(gid, 'cooldown', cooldown)[1] * 60
        self.count = 0
        self.time = 0

    def _getRemaining(self):
        return self.duration - (time.time() - self.time)

    def _setRemaining(self, value):
        self.time = time.time() - (self.duration - value)

    remaining = property(_getRemaining, _setRemaining)

    def __get__(self, instance, owner):
        if self.count==self.limit:
            return self.remaining
        else:
            self.count += 1
            return True
        if self.remaining <= 0:
            return True