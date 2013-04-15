#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import codecs


# Borrowed from
# https://github.com/jezdez/django_compressor/blob/develop/setup.py
def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='loom',
    version=find_version("loom", "__init__.py"),
    description='Elegant deployment with Fabric and Puppet.',
    author='Ben Firshman',
    author_email='ben@firshman.co.uk',
    url='http://github.com/bfirsh/loom',
    packages = ['loom'],
    package_data = {'loom': ['files/init/*', 'files/puppet/*']},
    install_requires = open('requirements.txt').readlines(),
    #test_suite = 'nose.collector',
)
