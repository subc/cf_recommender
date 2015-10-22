# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

DEFAULT_SETTINGS = {
            'expire': 3600 * 24 * 30,
            # redis
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 12
            }
        }
