Collaborative Filtering Real Time Recommender Engine
====================================================

It is a collaborative filtering type RealTime recommendation engine of open source that has been implemented in Python. The Amazon provides a "Customers who bought this product Customers who bought this product also purchased" function and, function similar to the "recommended users" feature of Twitter.

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

- Free untill Dec 1, 2015

- $1000 used for each product From Dec 1, 2015

For individual developers
*********************************************

Always Free



Documentation
-----------------

- get `GoogleAPI token`_

- `White Paper`_ in Qiita

.. _`GoogleAPI token`: http://www.php-factory.net/calendar_form/google_api.php
.. _`White Paper`: http://qiita.com/haminiku/items/3c8f0d43d82c0d58d7da
