#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2015 Bruno Adelé'
__description__ = """Unittest"""
__license__ = 'GPLv3'

import os
import sys
import shutil
from cStringIO import StringIO

import unittest
import git

from gitcheck import gitcheck

class TestPackages(unittest.TestCase):
    gitroot = '/tmp/gitcheck-unittest'

    def setUp(self):
        # Get projects
        self._get_github_projects("gitcheck", "git@github.com:badele/gitcheck.git")
        self._get_github_projects("serialkiller", "git@github.com:badele/serialkiller.git")
        self._get_github_projects("fabrecipes", "git@github.com:badele/fabrecipes.git")

        # Redirect stdout
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output


    def tearDown(self):
        # Reset stdout
        self.output.close()
        sys.stdout = self.saved_stdout

    def _get_github_projects(self, projectname, projecturl):
        # Preparing the git directory
        gitdir = "%s/%s" % (self.gitroot, projectname)

        if os.path.exists(gitdir):
            shutil.rmtree(gitdir)
        os.makedirs(gitdir)
        os.chdir(self.gitroot)

        # Get a git projects
        git.Git().clone(projecturl)

    def test_searchRepositories(self):
        os.chdir(self.gitroot)
        repos = gitcheck.searchRepositories()

        self.assertEqual(repos[0], '%s/fabrecipes' % self.gitroot)
        self.assertEqual(repos[1], '%s/gitcheck' % self.gitroot)
        self.assertEqual(repos[2], '%s/serialkiller' % self.gitroot)

    def test_gitcheck(self):
        os.chdir(self.gitroot)

        gitcheck.tcolor.DEFAULT = ""
        gitcheck.tcolor.BOLD = ""
        gitcheck.tcolor.RED = ""
        gitcheck.tcolor.GREEN = ""
        gitcheck.tcolor.BLUE = ""
        gitcheck.tcolor.ORANGE = ""
        gitcheck.tcolor.MAGENTA = ""
        gitcheck.tcolor.RESET = ""

        gitcheck.gitcheck()

        output = sys.stdout.getvalue().strip()
        lines = output.split('\n')

        self.assertEqual(lines[0], 'fabrecipes/master ')
        self.assertEqual(lines[1], 'gitcheck/master ')
        self.assertEqual(lines[2], 'serialkiller/master')

if __name__ == "__main__":
    unittest.main(verbosity=2)
