# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from cf_recommender.recommender import Recommender
import random
from uuid import uuid4


settings = {
    'expire': 3600 * 24 * 100
}

# register new goods
tags = ['default', 'book', 'computer', 'dvd', 'camera', 'clothes', 'tag7', 'tag8', 'tag9', 'tag10']
r = Recommender(settings)
for x in xrange(1, 100 * 10000):
    r.register(x, tag=random.choice(tags))

# like goods_ids
for x in xrange(1, 100 * 10000):
    user_id = str(uuid4())
    like_goods_ids = [random.randint(1, 100 * 10000) for x in range(random.randint(1, 100))]
    r.like(user_id, like_goods_ids)
