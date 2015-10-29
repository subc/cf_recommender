# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

DEFAULT_SETTINGS = {
            # redis
            'expire': 3600 * 24 * 30,
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0
            },
            # recommendation engine settings
            'recommendation_count': 10,
            'recommendation': {
                'update_interval_sec': 600,
                'search_depth': 100,
                'max_history': 1000,
            },
        }
