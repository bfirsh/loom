#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='loom',
    version='0.0.1',
    description='',
    author='',
    author_email='',
    url='http://github.com/bfirsh/loom',
    packages = [
        'loom'
    ],
    package_data = {},
    include_package_data=True,
    install_requires = open('requirements.txt').readlines(),
    entry_points={},
    #test_suite = 'nose.collector',
)

