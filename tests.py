# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from cf_recommender.recommender import Recommender
import random
from uuid import uuid4
from cf_recommender.repository import Repository

tags = ['default', 'book', 'computer', 'dvd', 'camera', 'clothes', 'tag7', 'tag8', 'tag9', 'tag10']


def test_recommender():
    settings = {
        'expire': 3600 * 24 * 100
    }
    r = Recommender(settings)

    register(r)
    like(r)
    get_all(r)
    update_index(r)


def register(r):
    # register
    goods_id = '12345'
    tag = 'default'
    r.register(goods_id, tag)
    assert r.repository.get_tag(goods_id) == tag, r.repository.get_tag(goods_id)

    # register new goods
    goods_id2 = 12131314324
    r.register(goods_id2, tag='dvd')

    # categorized
    cate = r.repository.categorized([goods_id, goods_id2, goods_id2])
    assert cate.get('default') == [goods_id]
    assert cate.get('dvd') == [str(goods_id2), str(goods_id2)]


def like(r):
    # like goods_ids
    user_id = str(uuid4())
    like_goods_ids = [random.randint(1, 100 * 10000) for x in range(random.randint(1, 100))]
    for goods_id in like_goods_ids:
        r.register(goods_id, random.choice(tags))
    r.like(user_id, like_goods_ids)


def get_all(r):
    # all registered goods ids: about 20sec
    r.get_all_goods_ids()

    # all user ids: about 20sec
    keys = r.repository.get_all_user_ids()
    if keys:
        Repository.get_user_and_key_from_redis_key(keys[0])


def update_index(r):
    user_id = str(uuid4())
    like_goods_ids = [random.randint(1, 100 * 10000) for x in range(random.randint(1, 100))]
    for goods_id in like_goods_ids:
        r.register(goods_id, random.choice(tags))
        # recreate index
        r.repository.recreate_index(goods_id, [str(uuid4()) for x in xrange(3)])

    # recreate all index: 1800sec
    r.recreate_all_index()
