#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='loom',
    version='0.0.4',
    description='Elegant deployment with Fabric and Puppet.',
    author='Ben Firshman',
    author_email='ben@firshman.co.uk',
    url='http://github.com/bfirsh/loom',
    packages = ['loom'],
    package_data = {'loom': ['files/init/*', 'files/puppet/*']},
    install_requires = open('requirements.txt').readlines(),
    #test_suite = 'nose.collector',
)

