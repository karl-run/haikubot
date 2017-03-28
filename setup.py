#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

config = {
    'name': 'Haikubot',
    'version': '0.1',
    'description': 'A simple Slackbot for collecting pull-request haiku.',
    'author': 'Karl J. Overå',
    'author_email': 'karl@karl.run',
    'license': 'LICENSE.md',
    'url': 'https://github.com/hermith/haikubot.',
    'download_url': 'https://github.com/hermith/haikubot/releases',
    'install_requires': ['slackclient', 'sqlalchemy'],
    'packages': find_packages(exclude=['tests']),
    'scripts': ['bin/run_haikubot.py']
}

setup(**config)
