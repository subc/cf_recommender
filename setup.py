from setuptools import setup
from cf_recommender import __version__
import os

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    name='cf_recommender',
    version=__version__,
    description='Real Time Recommendation System of Collaborative Filtering',
    long_description=long_description,
    author='haminiku',
    author_email='haminiku1129@gmail.com',
    url='https://github.com/subc/cf_recommender',
    packages=['cf_recommender'],
    package_dir={'cf_recommender': 'cf_recommender'},
    include_package_data=True,
    install_requires=['redis >= 2.9.1',
                      ],
    license='License :: Free For Home Use',
    zip_safe=False,
    keywords=['recommendation',
              'recommender',
              'cf',
              'Collaborative',
              'Collaborative Filtering'],
    classifiers=(
        'License :: Free For Home Use',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
)
