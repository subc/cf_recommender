# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from redis import Redis
from .settings import DEFAULT_SETTINGS

# redis key
PREFIX = 'CF_RECOMMENDER'
GOODS_TAG_BASE = '%s:GOODS:TAG:{}' % PREFIX
USER_LIKE_HISTORY_BASE = '%s:USER:LIKE-HISTORY:{}:{}' % PREFIX
INDEX_GOODS_USER_BASE = '%s:INDEX:GOODS-USER-LIKE-HISTORY:{}:{}' % PREFIX
GOODS_ALL = '%s:GOODS:ALL' % PREFIX

# redis TTL
PERSISTENT_SEC = 3600 * 24 * 365 * 1000


class GetALLMixin(object):
    def get_goods_all(self):
        return self.client.lrange(GOODS_ALL, 0, -1)

    def add_goods(self, goods_ids):
        goods_ids = [str(goods_id) for goods_id in goods_ids]
        self.client.rpush(GOODS_ALL, *goods_ids)
        return


class Repository(object):
    _cli = None
    _CACHE_GOODS_TAG = {}  # class cache

    def __init__(self, settings):
        DEFAULT_SETTINGS.update(settings)
        self.settings = DEFAULT_SETTINGS

    @classmethod
    def get_key_goods_tag(cls, goods_id):
        return GOODS_TAG_BASE.format(str(goods_id)).upper()

    @classmethod
    def get_key_user_like_history(cls, tag, user_id):
        return USER_LIKE_HISTORY_BASE.format(tag, user_id).upper()

    @classmethod
    def get_key_index_goods_user_like_history(cls, tag, goods_id):
        return INDEX_GOODS_USER_BASE.format(tag, str(goods_id)).upper()

    @classmethod
    def get_user_and_key_from_redis_key(cls, key):
        """
        >>> key = "CF_RECOMMENDER:USER:LIKE-HISTORY:BOOK:035A6959-B024-43CD-9FE9-5BCD4A0E5A92"
        >>> r = key.split(':')
        >>> r[3:]
        ['BOOK', '035A6959-B024-43CD-9FE9-5BCD4A0E5A92']
        :rtype : list[str]
        """
        r = key.split(':')
        return r[3:]

    def get_goods_tag(self, goods_id):
        tag = Repository._CACHE_GOODS_TAG.get(goods_id)
        if tag is None:
            tag = self.get_tag(goods_id)
            Repository._CACHE_GOODS_TAG[goods_id] = tag
        return tag

    def get_tag(self, goods_id):
        key = self.get_key_goods_tag(goods_id)
        return self.client.get(key)

    @property
    def client(self):
        if self._cli is None:
            self._cli = Redis(host=self.settings.get('redis').get('host'),
                              port=self.settings.get('redis').get('port'),
                              db=self.settings.get('redis').get('db'),)
        return self._cli

    @property
    def expire(self):
        return self.settings.get('expire')

    def goods_exist(self, goods_id):
        """
        already registered goods
        :param : str
        :rtype : bool
        """
        return bool(self.client.get(Repository.get_key_goods_tag(goods_id)))

    def register(self, goods_id, tag):
        """
        register goods_id
        :param goods_id: str
        :param tag: str
        :rtype : None
        """
        key = Repository.get_key_goods_tag(goods_id)
        return self.client.setex(key, tag, PERSISTENT_SEC)

    def like(self, user_id, goods_ids):
        """
        record user like history
        :param user_id: str
        :param goods_ids: list[str]
        :rtype : None
        """
        goods_group = self.categorized(goods_ids)
        for tag in goods_group:
            key = Repository.get_key_user_like_history(tag, user_id)
            self.client.rpush(key, *goods_ids)
        return

    def categorized(self, goods_ids):
        """
        :param dict{str: list[str]} goods_ids: dict{tag: list[goods_id]}
        :return:
        """
        result = defaultdict(list)
        for goods_id in goods_ids:
            result[self.get_tag(str(goods_id))] += [str(goods_id)]
        return result

    def update_index(self, user_id, goods_ids):
        """
        update goods index
        :param user_id: str
        :param goods_ids: list[str]
        :rtype : None
        """
        for goods_id in goods_ids:
            tag = self.get_tag(goods_id)
            key = Repository.get_key_index_goods_user_like_history(tag, goods_id)
            self.client.rpush(key, user_id)
        return

    def get_all_goods_ids(self):
        """
        all registered goods ids
        :rtype : list[str]
        """
        key = Repository.get_key_goods_tag('*')
        result = self.client.keys(key)
        del_word = GOODS_TAG_BASE[0:len(GOODS_TAG_BASE)-2]
        return map(lambda x: x.replace(del_word, ''), result)

    def get_all_user_ids(self):
        """
        all user ids
        :rtype : list[str]
        """
        key = Repository.get_key_user_like_history('*', '*')
        return self.client.keys(key)

    def get_user_like_history(self, user_id, tag):
        """
        :param user_id: str or unicode
        :rtype : list[str]
        """
        key = Repository.get_key_user_like_history(tag, user_id)
        num = self.settings.get('recommendation').get('user_history_count')
        result = self.client.lrange(key, -1 * num, -1)
        if not result:
            return []
        return result

    def recreate_index(self, goods_id, user_ids):
        """
        recreate goods_id liked users index
        :param goods_id: str
        :param user_ids: list[str or unicode]
        :rtype : None
        """
        if not user_ids:
            return
        tag = self.get_tag(goods_id)
        key = Repository.get_key_index_goods_user_like_history(tag, goods_id)
        print '@@@@@', key, user_ids
        # delete list
        self.client.delete(key)
        # update list
        self.client.rpush(key, *user_ids)
        return
