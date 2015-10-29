# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from .timeit import timeit
from .repository import Repository
from .default_settings import DEFAULT_SETTINGS

DEFAULT_TAG = 'default'


class Recommender(object):
    _r = None

    def __init__(self, settings):
        DEFAULT_SETTINGS.update(settings)
        self.settings = DEFAULT_SETTINGS

    @property
    def repository(self):
        if self._r is None:
            self._r = Repository(self.settings)
        return self._r

    def get(self, goods_id, count=None):
        return self.repository.get(goods_id, count=count)

    def update(self, goods_id):
        """
        update recommendation list
        :param goods_id: str
        """
        self.repository.update_recommendation(goods_id)
        return

    def register(self, goods_id, tag=DEFAULT_TAG):
        """
        register goods_id
        :param goods_id: int
        :param tag: str
        :rtype : None
        """
        return self.repository.register(goods_id, tag)

    def like(self, user_id, goods_ids, realtime_update=True, enable_update_interval=True):
        """
        record user like history
        :param str or unicode user_id: user_id
        :param list[int] goods_ids: list of goods_id
        :param bool realtime_update: update recommendation
        :param bool enable_update_interval: will update recommendation list at a constant interval
        :rtype : None
        """
        if type(goods_ids) in [int, long, str, unicode]:
            goods_ids = list(goods_ids)
        assert type(goods_ids) == list

        # like
        self.repository.like(user_id, goods_ids)

        # update index
        self.repository.update_index(user_id, goods_ids)

        # update recommendation list
        if realtime_update:
            for goods_id in goods_ids:
                self.repository.update_recommendation(goods_id, enable_update_interval=enable_update_interval)  # RealTime update

        return

    def get_all_goods_ids(self):
        """
        all registered goods ids
        WARNING!! this is heavy method about 1-100sec
        :rtype : list[int]
        """
        return self.repository.get_all_goods_ids()

    def update_all(self, proc=1, scope=None):
        """
        update all recommendation

        :param int proc: Multiprocess thread count
        :param tuple(list[int, int]) scope: update scope [start, partition count]
        :rtype : None
        """
        all_goods_ids = self.get_all_goods_ids()
        targets = all_goods_ids
        if scope:
            targets = slice_list(all_goods_ids, scope)
        for goods_id in targets:
            self.repository.update_recommendation(goods_id)

    def recreate_all_index(self):
        """
        update all index

        WARNING!! this method use high memory
        100,000 user >> memory 100MByte
        1,000,000 user >> memory 1GByte
        10,000,000 user >> memory 10GByte

        :rtype : None
        """
        # get all goods ids
        all_goods_ids = self.get_all_goods_ids()

        # get all user's like history
        all_users_like_history = self.get_all_users_like_history()

        # marge user's like history by goods_id
        for tag in all_users_like_history:
            hist = defaultdict(list)
            users_like_history = all_users_like_history.get(tag)
            for user_id in users_like_history:
                for goods_id in users_like_history[user_id]:
                    hist[goods_id] += [user_id]

            # recreate index
            for goods_id in all_goods_ids:
                if goods_id in hist:
                    self.repository.recreate_index(goods_id, hist[goods_id])

    def get_all_users_like_history(self):
        """
        :rtype : dict{str: list[int]}
        :rtype dict{str: dict{str: list[str]}} : dict{user_id: dict{tag:list[goods_id]}}
        """
        # get all user like history keys
        all_user_keys = self.repository.get_all_user_ids()

        result = defaultdict(dict)
        for key in all_user_keys:
            tag, user_id = Repository.get_user_and_key_from_redis_key(key)
            result[tag].update({user_id: self.repository.get_user_like_history(user_id, tag)})
        return result

    def remove_goods(self, goods_id):
        self.repository.remove_goods(goods_id)

    def update_goods_tag(self, goods_id, new_tag):
        self.remove_goods(goods_id)
        self.register(goods_id, tag=new_tag)

    def remove_user(self, user_id):
        self.repository.remove_user(user_id)


def slice_list(l, scope):
    if scope is None:
        return l
    if scope[1] <= 1:
        raise ValueError
    if scope[0] == scope[1]:
        raise ValueError
    if len(scope) != 2:
        raise AssertionError
    l.sort()
    length = len(l)
    _base = length / scope[1]
    start = max((_base * scope[0]) - 10, 0)
    finish = _base * (scope[0] + 1) + 10

    return l[start:finish]
