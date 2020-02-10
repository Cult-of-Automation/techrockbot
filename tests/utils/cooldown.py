import logging
import time

from tests.variables import _get

class ListenerCooldown(object):
    
    def __init__(self, gid, cd_name):
        self.limit = _get(gid, 'cooldown', cd_name)[1]
        self.duration = _get(gid, 'cooldown', cd_name)[2] * 60
        self.count = 0
        self.time = time.time() + self.duration

    def __call__(self):

        if time.time() < self.time:
            self.count += 1
        else:
            # Reset count
            self.count = 0
            self.time = time.time() + self.duration

        if self.count == self.limit:
            return None
        elif self.count < self.limit:
            return True
        elif self.count > self.limit:
            return False