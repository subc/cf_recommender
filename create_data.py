# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from cf_recommender.recommender import Recommender
import random
from uuid import uuid4


settings = {
    'expire': 3600 * 24 * 100,
    # redis
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 11
    },
}

_MAX = 1 * 50000

# register new goods
tags = ['default', 'book', 'computer', 'dvd', 'camera', 'clothes', 'tag7', 'tag8', 'tag9', 'tag10']
r = Recommender(settings=settings)
for x in xrange(1, _MAX):
    r.register(x, tag=random.choice(tags))

# like goods_ids
for x in xrange(1, _MAX):
    user_id = str(uuid4())
    like_goods_ids = [random.randint(1, _MAX) for _x in range(random.randint(1, 100))]
    r.like(user_id, like_goods_ids, realtime_update=False)
    if x % 100 == 0:
        print "{}/{}".format(str(x), str(_MAX))
