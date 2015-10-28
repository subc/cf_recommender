# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
import random
from redis import Redis
from .default_settings import DEFAULT_SETTINGS
from .mutex import Lock

# redis key
PREFIX = 'CF'
GOODS_TAG_BASE = '%s:GOODS:TAG:{}' % PREFIX
USER_LIKE_HISTORY_BASE = '%s:USER:LIKE-HIS:{}:{}' % PREFIX
INDEX_GOODS_USER_BASE = '%s:INDEX:GOODS-HIS:{}:{}' % PREFIX
GOODS_RECOMMENDATION = '%s:GOODS:RECO:{}:{}' % PREFIX
GOODS_MUTEX = '%s:GOODS:MUTEX:{}:{}' % PREFIX

# redis hash key
HASH_FIELD_GOODS_TAG = "TAG"


class Repository(object):
    _CACHE_GOODS_TAG = {}  # class cache
    _CLI = None

    def __init__(self, settings=DEFAULT_SETTINGS):
        DEFAULT_SETTINGS.update(settings)
        self.settings = DEFAULT_SETTINGS

    @classmethod
    def get_key_goods_tag(cls, goods_id):
        return GOODS_TAG_BASE.format(str(goods_id))

    @classmethod
    def get_key_user_like_history(cls, tag, user_id):
        return USER_LIKE_HISTORY_BASE.format(tag, user_id)

    @classmethod
    def get_key_index_goods_user_like_history(cls, tag, goods_id):
        return INDEX_GOODS_USER_BASE.format(tag, str(goods_id))

    @classmethod
    def get_key_goods_recommendation(cls, tag, goods_id):
        return GOODS_RECOMMENDATION.format(tag, str(goods_id))

    @classmethod
    def get_key_goods_mutex(cls, tag, goods_id):
        return GOODS_MUTEX.format(tag, str(goods_id))

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

    @property
    def client(self):
        if Repository._CLI is None:
            Repository._CLI = Redis(host=self.settings.get('redis').get('host'),
                                    port=int(self.settings.get('redis').get('port')),
                                    db=int(self.settings.get('redis').get('db')), )
        return Repository._CLI

    @property
    def expire(self):
        return self.settings.get('expire')

    def touch(self, key):
        self.client.expire(key, self.expire)

    def get(self, goods_id, count=None):
        """
        get recommendation list
        :param goods_id: str
        :param count: int
        :rtype list[str]: list of recommendation goods
        """
        if not count:
            count = self.settings.get('recommendation_count')
        tag = self.get_tag(goods_id)
        key = Repository.get_key_goods_recommendation(tag, goods_id)
        self.touch(key)
        return self.client.zrevrange(key, 0, count - 1)

    def get_goods_tag(self, goods_id):
        tag = Repository._CACHE_GOODS_TAG.get(goods_id)
        if tag is None:
            tag = self.get_tag(goods_id)
            Repository._CACHE_GOODS_TAG[goods_id] = tag
        return tag

    def get_tag(self, goods_id):
        key = self.get_key_goods_tag(goods_id)
        return self.client.hget(key, HASH_FIELD_GOODS_TAG)

    def register(self, goods_id, tag):
        """
        register goods_id
        :param goods_id: str
        :param tag: str
        :rtype : None
        """
        key = Repository.get_key_goods_tag(goods_id)
        return self.client.hset(key, HASH_FIELD_GOODS_TAG, tag)

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
            _goods_ids = goods_group[tag]
            if _goods_ids:
                self.client.rpush(key, *_goods_ids)
            self.touch(key)
            self.trim(key)
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

    def update_recommendation(self, goods_id, enable_update_interval=False):
        """
        Update goods recommendation list.
        If enable_update_interval is True, will update recommendation list at a constant interval

        :param goods_id: str
        :param enable_update_interval: bool
        """
        tag = self.get_tag(goods_id)
        if tag is None:
            return  # goods doesn't exist

        # will update at a constant interval
        if enable_update_interval:
            if self.is_lock(goods_id):
                return
            self.lock(goods_id)

        # get user
        users = self.get_goods_like_history(goods_id)

        # calc recommendation
        recommendation_list = []
        for user_id in users:
            recommendation_list += self.get_user_like_history(user_id, tag)

        result = defaultdict(int)
        for _tmp_goods_id in recommendation_list:
            tag = self.get_tag(_tmp_goods_id)
            if tag is None:
                continue

            if _tmp_goods_id == goods_id:
                continue
            result[_tmp_goods_id] += 1

        # set sorted set of redis
        key = Repository.get_key_goods_recommendation(tag, goods_id)
        self.client.delete(key)
        for _tmp_goods_id in result:
            self.push_recommendation(key, _tmp_goods_id, result[_tmp_goods_id])
        return

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
            self.trim(key)
        return

    def get_goods_like_history(self, goods_id, count=None):
        """
        :param goods_id: str
        :param count: int
        :rtype list[str]: liked users of goods
        """
        if not count:
            count = self.settings.get('recommendation').get('search_depth')
        tag = self.get_tag(goods_id)
        key = Repository.get_key_index_goods_user_like_history(tag, goods_id)
        return self.client.lrange(key, -1 * count, -1)

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

    def get_user_like_history(self, user_id, tag, count=None):
        """
        :param user_id: str or unicode
        :rtype list[str]: goods_ids of user
        """
        if not count:
            count = self.settings.get('recommendation').get('search_depth')
        key = Repository.get_key_user_like_history(tag, user_id)
        result = self.client.lrange(key, -1 * count, -1)
        if not result:
            return []
        return result

    def push_recommendation(self, key, goods_id, value):
        """
        update recommendation sorted set
        :param str goods_id:
        :param str value: count
        """
        self.client.zadd(key, goods_id, int(value))
        self.touch(key)

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
        self.client.delete(key)
        # update list
        self.client.rpush(key, *user_ids)
        return

    def get_all_goods_by_user(self, user_id):
        """
        get all liked goods by user
        :param user_id: str
        :rtype: list[goods_id]
        """
        keys_asterisk_pattern = Repository.get_key_user_like_history('*', user_id)
        keys = self.client.keys(keys_asterisk_pattern)
        goods_history = []
        for key in keys:
            goods_history += self.client.lrange(key, 0, -1)
        return goods_history

    def remove_goods(self, goods_id):
        # remove goods tag and recommendation
        tag = self.get_goods_tag(goods_id)
        key_tag = Repository.get_key_goods_tag(goods_id)
        key_recommendation = Repository.get_key_goods_recommendation(tag, goods_id)
        self.client.delete(key_tag, key_recommendation)
        self.client.delete(key_recommendation)

        # delete tag cache
        del Repository._CACHE_GOODS_TAG[goods_id]
        return

    def remove_user(self, user_id):
        """
        remove user
        :param user_id: str
        """
        # get user's redis key
        keys_asterisk_pattern = Repository.get_key_user_like_history('*', user_id)
        keys = self.client.keys(keys_asterisk_pattern)
        users_goods = self.get_all_goods_by_user(user_id)

        # delete user from index
        self.remove_user_from_index(user_id, users_goods)

        # delete user from history
        for key in keys:
            self.client.delete(key)

    def remove_user_from_index(self, user_id, goods_ids):
        """
        remove user from INDEX_GOODS_USER_BASE
        :param user_id: str
        :param goods_ids: list[str]
        """
        for goods_id in goods_ids:
            tag = self.get_goods_tag(goods_id)
            key = Repository.get_key_index_goods_user_like_history(tag, goods_id)
            self.client.lrem(key, user_id, 0)
        return

    def lock(self, goods_id, interval_sec=None):
        """
        When interval_sec is 0, not lock.
        :param goods_id: str
        :rtype : None
        """
        if interval_sec is None:
            interval_sec = self.settings.get('recommendation').get('update_interval_sec')
        if interval_sec == 0:
            return

        tag = self.get_goods_tag(goods_id)
        key = Repository.get_key_goods_mutex(tag, goods_id)
        self.get_lock(key, interval_sec).lock()
        return

    def is_lock(self, goods_id):
        """
        :param goods_id: str
        :rtype : bool
        """
        # When interval_sec is 0, not lock.
        if self.settings.get('recommendation').get('update_interval_sec') == 0:
            return False

        tag = self.get_goods_tag(goods_id)
        key = Repository.get_key_goods_mutex(tag, goods_id)
        return self.get_lock(key, 1).is_lock()

    def get_lock(self, key, interval_sec):
        """
        get Lock object
        :param key: str
        :param interval_sec: int
        :rtype : Lock
        """
        return Lock(self.client, key, interval_sec)

    def trim(self, key, _max=None, hardly_ever=True):
        """
        trim redis list data object
        :param str key:
        :param int _max: Trim Redis list If the max value is over
        :param bool hardly_ever: bool
        :rtype: None
        """
        if hardly_ever and random.randint(1, 20) != 1:
            return

        if _max is None:
            _max = self.settings.get('recommendation').get('max_history')

        if self.client.llen(key) < _max * 2:
            return
        self.client.ltrim(key, _max * -1, -1)
        return
