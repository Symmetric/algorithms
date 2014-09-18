#!/usr/bin/env python

from distutils.core import setup

setup(
    name='algorithms',
    version='0.1.0',
    description='Algorithm explorations',
    author='Paul Tiplady',
    author_email='paul.tiplady@gmail.com',
    url='http://github.com/symmetric/algorithms',
    packages=['graphs'],
    # scripts=[
    #     # 'graphs/kevin_bacon.py'
    # ],
    entry_points={
        'console_scripts': [
            'kevin_bacon = graphs.kevin_bacon:main',
        ],
    }
)