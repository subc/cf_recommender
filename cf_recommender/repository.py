# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from redis import Redis
from .settings import DEFAULT_SETTINGS

# redis key
GOODS_TAG_BASE = 'CF_RECOMMENDER:GOODS:TAG:{}'
USER_LIKE_HISTORY_BASE = 'CF_RECOMMENDER:USER:LIKE-HISTORY:{}'
INDEX_GOODS_USER_BASE = 'CF_RECOMMENDER:INDEX:GOODS:USER:LIKE-HISTORY:{}'


class Repository(object):
    _cli = None

    def __init__(self, settings):
        DEFAULT_SETTINGS.update(settings)
        self.settings = DEFAULT_SETTINGS

    @classmethod
    def get_key_goods_tag(cls, goods_id):
        return GOODS_TAG_BASE.format(str(goods_id))

    @classmethod
    def get_key_user_like_history(cls, user_id):
        return USER_LIKE_HISTORY_BASE.format(user_id)

    @classmethod
    def get_key_index_goods_user_like_history(cls, goods_id):
        return INDEX_GOODS_USER_BASE.format(str(goods_id))

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
        return self.client.setex(key, tag, self.expire)

    def like(self, user_id, goods_ids):
        """
        record user like history
        :param user_id: str
        :param goods_ids: list[str]
        :rtype : None
        """
        key = Repository.get_key_user_like_history(user_id)
        goods_ids = [str(_id) for _id in goods_ids]
        return self.client.rpush(key, *goods_ids)

    def update_index(self, user_id, goods_ids):
        """
        update goods index
        :param user_id: str
        :param goods_ids: list[str]
        :rtype : None
        """
        for goods_id in goods_ids:
            key = Repository.get_key_index_goods_user_like_history(goods_id)
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
        key = Repository.get_key_user_like_history('*')
        result = self.client.keys(key)
        del_word = USER_LIKE_HISTORY_BASE[0:len(USER_LIKE_HISTORY_BASE)-2]
        return map(lambda x: x.replace(del_word, ''), result)

    def get_user_like_history(self, user_id):
        """
        :param user_id: str or unicode
        :rtype : list[str]
        """
        key = Repository.get_key_user_like_history(user_id)
        # result = self.client.get(key)
        # ToDo read settings value
        result = self.client.lrange(key, -1000, -1)
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
        print "recreate_index: ", goods_id, user_ids

        key = Repository.get_key_index_goods_user_like_history(goods_id)
        # delete list
        self.client.delete(key)
        # update list
        self.client.rpush(key, *user_ids)
        return
