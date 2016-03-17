Collaborative Filtering Real Time Recommender Engine
====================================================

It is a collaborative filtering type RealTime recommendation engine of open source that has been implemented in Python. The Amazon provides a "Customers who bought this product Customers who bought this product also purchased" function and, function similar to the "recommended users" feature of Twitter.

- 日本語ドキュメント: `Japanese Document`_

Features
--------
- get fast within 10ms
- Real time updating recommendation list 
- easy install
- High versatility
- Tags Support

Installation
-----------------

.. code-block:: bash

    $ pip install cf_recommender

Sample Code
-----------------

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    
    cf_settings = {
        # redis
        'expire': 3600 * 24 * 30,
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        # recommendation engine settings
        'recommendation_count': 10,
        'recommendation': {
            'update_interval_sec': 600,
            'search_depth': 100,
            'max_history': 1000,
        },
    }
    
    
    # Get recommendation list
    item_id = 'Item1'
    recommendation = Recommender(cf_settings)
    print recommendation.get(item_id, count=3)
    >>> ['Item10', 'Item3', 'Item2']
    
    # register history
    user_id = 'user-00001'
    buy_items = ['Item10', 'Item10', 'Item10', 'Item3', 'Item3', 'Item1']
    for item_id in buy_items:
        recommendation.register(item_id)
    recommendation.like(user_id, buy_items)


    ...

Recommendation Algorithms
---------------------------------------------------
Determine the recommendation target by simple co-occurrence. Ratings are often items will be highly appreciated. For example, among the Item1-10, 51% of 100 people user the purchase history of Item10, when the remaining 49% were bought at random, then appeared Item10 with a high probability as the top recommendation of Item1-9.

Concrete example
************************************

We will mention about the logic to determine the recommendation subject to the specific case of Item-3. Expand the latest Item3 purchase user on the 100 persons memory, to create a product purchase list by referring to the latest purchase history 100 cases of purchase user. From the total of items purchased covers the entire history and register as a recommendation subject to the order. The depth of the search can be changed in settings.recommendation.search_depth. default value is set to 100. When the epidemic is shifted Item1 is purchased in large quantities history is updated Item1 will now appear as the top recommendation. The depth of the search it will affect the transition speed of the product to be recommended. Please tune so that it is appropriate recommendation which the product will seek.

Tutorial
---------------------------------------------------

1. you want to install the 1.redis to local PC.
2. start the 2.redis.
3. In 3.redis-cli command I do communication confirmation.

.. code-block:: bash

    (env)niku > redis-cli
    redis 127.0.0.1:6379> set a 1
    OK
    redis 127.0.0.1:6379> get a
    "1"

4. install a cf-recommender

.. code-block:: bash

    $ pip install cf_recommender

5. Create and run a py file written sample code

.. code-block:: bash

    (env)niku > python cf.py 
    []
    ['Item10', 'Item3', 'Item2']
    (env)niku > python cf.py 
    ['Item10', 'Item3', 'Item2']
    ['Item10', 'Item3', 'Item2']


Settings
-----------------

.. image:: https://qiita-image-store.s3.amazonaws.com/0/65312/7329c185-0015-02b9-98fb-e3abc62be6b0.png
    :alt: HTTPie compared to cURL
    :align: center

Redis Data structure
----------------------------------

.. image:: https://qiita-image-store.s3.amazonaws.com/0/65312/4bb5c5d4-a7b0-3a5e-1b30-854377cf75a1.png
    :alt: HTTPie compared to cURL
    :align: center


Sample1 Django: Player to Player Recommendation 
-----------------------------------------------------------------

.. code-block:: python

    # Django - Model
    # -*- coding: utf-8 -*-
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    from django.conf import settings


    class GuildRecommendation(object):
        cf = None

        def __init__(self):
            self.cf = Recommender(settings.ANALYTICS_REDIS_SETTINGS)

        def like(self, player_id, guild_ids):
            """
            :param player_id: str
            :param guild_ids: list of int
            """
            for guild_id in guild_ids:
                self.cf.register(guild_id)
            self.cf.like(player_id, guild_ids)

        def gets(self, guild_id, count=5):
            return self.cf.get(guild_id, count=count)

.. code-block:: python

    # Django - View
    # register
    GuildRecommendation().like(player.id, [guild_id])

    # get recommendation guild
    GuildRecommendation().gets(guild_id, count=20)
    >>> [8, 4, 3]


Sample2 Item Remove and Item Update Tag
-----------------------------------------------------------------

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender


    r = Recommender(settings={})

    user_id = "user1"
    goods_id = "Item1"

    """
    Purchase information of the user is deleted from INDEX, also INDEX to the user as garbage data 
    if some exist {recommendation.max_history} or more,  however the user's purchase 
    history of the user's purchase history is deleted history does not already exist continue remaining purchase history
    """
    r.remove_user(user_id)

    r.remove_goods(goods_id)
    r.update_goods_tag(goods_id, "book")



Sample3-1 Published from accumulating the data
-----------------------------------------------------------------

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender

    # register
    user_id = 'user-00001'
    buy_items = ['Item10', 'Item10', 'Item10', 'Item3', 'Item3', 'Item1']
    for item_id in buy_items:
        recommendation.register(item_id)
    recommendation.like(user_id, buy_items)


Sample3-2 Registered in the bulk data
-----------------------------------------------------------------

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    import random


    # register all goods
    tags = ['default', 'book', 'computer', 'dvd', 'camera', 'clothes', 'tag7', 'tag8', 'tag9', 'tag10']
    settings = {}
    r = Recommender(settings=settings)
    goods_ids = range(1, 1000)
    for goods_id in goods_ids:
        r.register(goods_id, tag=random.choice(tags))

    # register all users history 
    users = {
        'player1': [100, 200, 300],
        'player2': [100, 200, 300],
        'player3': [200, 300, 500],
        'player4': [500, 600, 700],
        'player5': [300, 400, 500],
    }

    ct = 0
    for user_id in users:
        like_goods_ids = users.get(user_id)
        # register by not updating recommendation
        r.like(user_id, like_goods_ids, realtime_update=False)
        if ct % 100 == 0:
            print "{}/{}".format(str(ct), str(len(users)))
        ct += 1

    # create index heavy memory use
    r.recreate_all_index()

    # create all recommendation about [100-500ms x item count]
    r.update_all()


Sample4 Worker Model
-----------------------------------------------------------------

When implemented in the worker model can be updated to distribute the products list that recommendation. The update of the whole recommendation list needs time items x100~500ms. In order to remove the deleted items from the recommendation list of other goods it was implemented because it requires re-generation of the total recommendation list. Also it can be calculated by distributing the listing generated for recommendation when new installations, it is assumed to be used when collectively changing the tag information of the product.

.. image:: https://qiita-image-store.s3.amazonaws.com/0/65312/14dc0f4d-85e2-69db-34c8-467a9adcb299.png
    :alt: HTTPie compared to cURL
    :align: center

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender

    # register
    user_id = 'user-00001'
    buy_items = ['Item10', 'Item10', 'Item10', 'Item3', 'Item3', 'Item1']
    for item_id in buy_items:
        recommendation.register(item_id)
    # update by not updating recommendation
    recommendation.like(user_id, buy_items, realtime_update=False)

.. code-block:: python

    # worker 1
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    Recommender(settings).update_all(scope=(0, 4))

.. code-block:: python

    # worker 2
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    Recommender(settings).update_all(scope=(1, 4))

.. code-block:: python

    # worker 3
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    Recommender(settings).update_all(scope=(2, 4))

.. code-block:: python

    # worker 4
    from __future__ import absolute_import, unicode_literals
    from cf_recommender.recommender import Recommender
    Recommender(settings).update_all(scope=(3, 4))


If you move the worker in supervisord it moves to feel good. scope = (0, 4) and 4 split all items list that was sort When set to update the recommendation list according to the goods in the first half of the quarter.

Tuning Recommendation
----------------------------------

1. I want to enable real-time update feature
    The default setting real-time update feature is turned OFF. Please be set to 0. To 'recommendation.update_interval_sec' to enable. However, whether the APP server at the time of the spike to secure sufficient resources because there is likely to die, please set the update interval to 5 seconds.

2. changes immediately goods to be recommended
    Please strengthen the history search of past direction by increasing to the To calm 'recommendation.search_depth' changes. However CPU load for calculation time is extended will increase.

3. Product is recommended does not update quickly
    Please set a short update interval of the product that is recommended by changing the 'recommendation.update_interval_sec'. The default value is 10 minutes.

4. I want to add a long time ago were popular items in the list recommend
    It can be achieved by extending the 'recommendation.search_depth and recommendation.max_history'. When the change since there is a possibility that the calculation time is extended big Please execute enough test. To generate a recommendation list in the worker as implementation 4 as a measure of computational time bloated, there is a way to stop the real-time update.


Trouble Shooting
----------------------------------

1. App Server CPU 100%
   
  'Recommender.like' is the recommendation is likely that takes time in the Product List generation process in the function. Let's review the following settings.

  a. 'recommendation.update_interval_sec' of the extended time to raise the update interval.

  b. Reduce the value of 'recommendation.search_depth', we want to reduce the amount of calculation when the commodity list generation that recommendation.

2. Over Redis max memory 

  a. lower the value of 'expire'. When the period expires, goods list to recommendation that has not been read even once during the period will be deleted.

  b. it reduces the value of the 'recommendation.max_history'. Past purchase history that overflowed is lost.


Bench Mark
-----------------

.. image:: https://qiita-image-store.s3.amazonaws.com/0/65312/d68405e8-900d-1dab-b92e-bc0df8ac08a7.png
    :alt: HTTPie compared to cURL
    :align: center

.. image:: https://qiita-image-store.s3.amazonaws.com/0/65312/6e6810eb-d9d3-959e-9561-5a04ea7d3edc.png
    :alt: HTTPie compared to cURL
    :align: center


License
-----------------

License :: Free For Home Use

For companies and organizations
*********************************************

Commercial License

Commercial Licenses are available to legal entities, including companies and organizations (both for-profit and non-profit), which require the software for general commercial use.

`PayPal here`_

For individual developers
*********************************************

Always Free



Documentation
-----------------


- `Japanese Document`_ in Qiita

.. _`Japanese Document`: http://qiita.com/haminiku/items/0cdf006d667ef8a7494e
.. _`PayPal here`: http://subc.github.io/payment/cf_recommender.html
