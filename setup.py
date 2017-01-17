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


install_requires = [
    'gitpython',
    'colored'
    ]

tests_require = install_requires + [
     'pep8',
     'coveralls',
]


setup(
    name='gitcheck',
    version='0.3.22',
    description='Check multiple git repository in one pass',
    long_description=rst('README.rst') + rst('CHANGELOG.txt'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
    ],
    author='Bruno Adele',
    author_email='bruno@adele.im',
    license='GPL',
    url='https://github.com/badele/gitcheck',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
    py_modules=['gitcheck.gitcheck',],
    entry_points={
        'console_scripts': ['gitcheck = gitcheck.gitcheck:main']
    }
)
