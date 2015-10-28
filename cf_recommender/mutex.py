# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class Lock(object):
    def __init__(self, client, key, expire):
        self._r = client
        self.key = key
        self.expire = expire

    def lock(self):
        self._r.setex(self.key, 1, self.expire)

    def unlock(self):
        self._r.delete(self.key)

    def is_lock(self):
        return bool(self._r.get(self.key))
