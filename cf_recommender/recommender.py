# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from .timeit import timeit
from .exception import RegisteredError
from .repository import Repository
from .settings import DEFAULT_SETTINGS

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

    def register(self, goods_id, tag=DEFAULT_TAG):
        """
        register goods_id
        :param goods_id: int
        :param tag: str
        :rtype : None
        """
        return self.repository.register(goods_id, tag)

    def like(self, user_id, goods_ids):
        """
        record user like history
        :param user_id: str
        :param goods_ids: list[int]
        :rtype : None
        """
        # like
        self.repository.like(user_id, goods_ids)

        # create index
        self.repository.update_index(user_id, goods_ids)

        return

    def get_all_goods_ids(self):
        """
        all registered goods ids
        WARNING!! this is heavy method about 1-100sec
        :rtype : list[int]
        """
        return self.repository.get_all_goods_ids()

    def update_all(self, proc=1, scope=(1, 1)):
        """
        update all recommendation

        :param int proc: Multiprocess thread count
        :param tuple(list[int, int]) scope: update scope [start, partition count]
        :rtype : None
        """
        pass

    @timeit
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
        # print all_users_like_history

        # marge user's like history by goods_id
        hist = defaultdict(list)
        for user_id in all_users_like_history:
            for goods_id in all_users_like_history[user_id]:
                hist[goods_id] += [user_id]

        # recreate index
        for goods_id in all_goods_ids:
            self.repository.recreate_index(goods_id, hist[goods_id])

    def get_all_users_like_history(self):
        """
        :rtype : dict{str: list[int]}
        :rturn : dict{user_id: list of goods_id}
        """
        # get all user like history keys
        all_user_ids = self.repository.get_all_user_ids()

        result = {}
        for user_id in all_user_ids:
            result[user_id] = self.repository.get_user_like_history(user_id)
        return result
