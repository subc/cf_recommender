# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from cf_recommender.recommender import Recommender
import random
from uuid import uuid4
from cf_recommender.repository import Repository
from cf_recommender.timeit import timeit

tags = ['default', 'book', 'computer', 'dvd', 'camera', 'clothes', 'tag7', 'tag8', 'tag9', 'tag10']


def test_recommender():
    settings = {
        'expire': 3600 * 24 * 100
    }
    r = Recommender(settings)

    normal_test(r)
    register(r)
    like(r)
    get_all(r)
    update_index(r)
    data_consistency(r)
    del_data_user(r)
    del_data_goods(r)


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
    like_goods_ids = [random.randint(1, 100 * 10000) for x in range(random.randint(1, 100))]
    for goods_id in like_goods_ids:
        r.register(goods_id, random.choice(tags))
        # recreate index
        r.repository.recreate_index(goods_id, [str(uuid4()) for x in xrange(3)])

    # recreate all index: 1800sec
    r.recreate_all_index()

    # update all
    r.update_all()


@timeit
def data_consistency(r):
    # register
    goods_ids = ['Book-X', 'Book-A', 'Book-B', 'Book-C', 'Book-D', 'Book-E']
    for goods_id in goods_ids:
        r.register(goods_id, 'book')

    # create users
    users = [
        ['A', ['Book-{}'.format(x) for x in ['X', 'B']]],
        ['B', ['Book-{}'.format(x) for x in ['A', 'B', 'C']]],
        ['C', ['Book-{}'.format(x) for x in ['X', 'B', 'C', 'D']]],
        ['D', ['Book-{}'.format(x) for x in ['A', 'C', 'E']]],
        ['E', ['Book-{}'.format(x) for x in ['X', 'A']]],
        ['F', ['Book-{}'.format(x) for x in ['E']]],
        ['G', ['Book-{}'.format(x) for x in ['C', 'E']]],
    ]

    # like
    for user, hist in users:
        # r.remove_like(user)
        r.like(user, hist)

    # get
    answer = {
        'Book-X': ['Book-{}'.format(x) for x in ['B']],
        'Book-A': ['Book-{}'.format(x) for x in ['C']],
        'Book-B': ['Book-{}'.format(x) for x in []],
        'Book-C': ['Book-{}'.format(x) for x in []],
        'Book-D': ['Book-{}'.format(x) for x in []],
        'Book-E': ['Book-{}'.format(x) for x in ['C']],
    }

    for goods_id in goods_ids:
        r.update(goods_id)
        print goods_id, r.get(goods_id, count=1)
        if len(answer.get(goods_id)):
            print answer.get(goods_id)
            assert r.get(goods_id, count=1)[0] == answer.get(goods_id)[0]


@timeit
def normal_test(r):
    # register
    goods_ids = ['DVD-1', 'DVD-2', 'DVD-3', 'DVD-4']
    for goods_id in goods_ids:
        r.register(goods_id, 'dvd')

    # like
    for x in xrange(1000):
        user_id = str(uuid4())
        hist = []
        hist.append(goods_ids[0])
        if random.randint(1, 2) == 1:
            hist.append(goods_ids[1])
        if random.randint(1, 4) == 1:
            hist.append(goods_ids[2])
        if random.randint(1, 8) == 1:
            hist.append(goods_ids[3])
        r.like(user_id, hist, realtime_update=False)
    r.like(user_id, hist, realtime_update=True)

    # update recommendation and check recommendation order
    for goods_id in goods_ids:
        r.update(goods_id)
        if goods_id == goods_ids[0]:
            assert r.get(goods_id, count=3)[0:3] == goods_ids[1:]
        else:
            assert r.get(goods_id, count=1)[0] == goods_ids[0]

    # test get
    goods_id = goods_ids[0]
    assert len(r.get(goods_id, count=1)) == 1
    assert len(r.get(goods_id, count=2)) == 2
    assert len(r.get(goods_id, count=3)) == 3


def del_data_user(r):
    pass


def del_data_goods(r):
    pass
