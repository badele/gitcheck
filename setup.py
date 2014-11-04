#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup

PYPI_RST_FILTERS = (
    # Replace code-blocks
    (r'\.\.\s? code-block::\s*(\w|\+)+', '::'),
    # Replace image
    (r'\.\.\s? image::.*', ''),
    # Remove travis ci badge
    (r'.*travis-ci\.org/.*', ''),
    # Remove pypip.in badges
    (r'.*pypip\.in/.*', ''),
    (r'.*crate\.io/.*', ''),
    (r'.*coveralls\.io/.*', ''),
)


def rst(filename):
    '''
Load rst file and sanitize it for PyPI.
Remove unsupported github tags:
- code-block directive
- travis ci build badge
'''
    content = open(filename).read()
    for regex, replacement in PYPI_RST_FILTERS:
        content = re.sub(regex, replacement, content)
    return content


setup(
    name='gitcheck',
    version='0.3.14',
    description='Check multiple git repository in one pass',
    long_description=rst('README.rst'),

    author='Bruno Adele',
    author_email='bruno@adele.im',
    license='GPL',
    url='https://github.com/badele/gitcheck',
    setup_requires=[],
    tests_require=[],
    py_modules=['gitcheck',],
    entry_points={
        'console_scripts': ['gitcheck = gitcheck:main']
    }
)
