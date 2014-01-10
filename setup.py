"""Setup file to generate a distribution of njord

usage:    python setup.py sdist
          python setup.py install
"""

from setuptools import setup

setup(name = 'gitcheck',
      version = '0.5',
      description = 'Check multiple git repository in one pass',
      long_description = "README.md",

      author = 'Bruno Adele',
      author_email = 'bruno.adele@jesuislibre.org',
      url = 'https://github.com/badele/gitcheck',
      py_modules = ['gitcheck'],
      entry_points={'console_scripts':['gitcheck = gitcheck:main'] }
     )
