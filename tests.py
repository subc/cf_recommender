# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from cf_recommender.recommender import Recommender
import random
from uuid import uuid4


def test_recommender():
    settings = {
        'expire': 3600 * 24 * 100
    }

    # register new goods
    tags = ['default', 'book', 'computer', 'dvd', 'camera', 'clothes', 'tag7', 'tag8', 'tag9', 'tag10']
    goods_id = 1
    r = Recommender(settings)
    r.register(goods_id, tag=random.choice(tags))

    # like goods_ids
    user_id = str(uuid4())
    like_goods_ids = [random.randint(1, 100 * 10000) for x in range(random.randint(1, 100))]
    r.like(user_id, like_goods_ids)

    # recreate index
    r.repository.recreate_index(116871, [str(uuid4()) for x in xrange(3)])

    # recreate all index: 1800sec
    r.recreate_all_index()

    # all registered goods ids: about 20sec
    r.get_all_goods_ids()

    # all user ids: about 20sec
    r.repository.get_all_user_ids()
