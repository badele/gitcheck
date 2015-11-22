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

GITROOT = '/tmp/gitcheck-unittest'


def setUpModule():
    # Get projects
    get_github_projects("gitcheck", "https://github.com/badele/gitcheck.git")
    get_github_projects("serialkiller", "https://github.com/badele/serialkiller.git")
    get_github_projects("fabrecipes", "https://github.com/badele/fabrecipes.git")


def get_github_projects(projectname, projecturl):
    # Preparing the git directory
    gitdir = "%s/%s" % (GITROOT, projectname)

    if os.path.exists(gitdir):
        shutil.rmtree(gitdir)
    os.makedirs(gitdir)
    os.chdir(GITROOT)

    # Get a git projects
    print "Get git %s project" % projectname
    git.Git().clone(projecturl)


class TestPackages(unittest.TestCase):
    def setUp(self):
        # Redirect stdout
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output


    def tearDown(self):
        # Reset stdout
        self.output.close()
        sys.stdout = self.saved_stdout


    def test_searchRepositories(self):
        os.chdir(GITROOT)
        repos = gitcheck.searchRepositories()

        self.assertEqual(repos[0], '%s/fabrecipes' % GITROOT)
        self.assertEqual(repos[1], '%s/gitcheck' % GITROOT)
        self.assertEqual(repos[2], '%s/serialkiller' % GITROOT)

    def test_gitcheck(self):
        os.chdir(GITROOT)

        defaulttheme = ""
        gitcheck.colortheme = {
            'default': defaulttheme,
            'prjchanged': defaulttheme,
            'prjremote': defaulttheme,
            'prjname': defaulttheme,
            'reponame': defaulttheme,
            'branchname': defaulttheme,
            'fileupdated': defaulttheme,
            'remoteto': defaulttheme,
            'committo': defaulttheme,
            'commitinfo': defaulttheme,
            'commitstate': defaulttheme,
            'bell': defaulttheme,
            'reset': defaulttheme,
        }

        gitcheck.gitcheck()

        output = sys.stdout.getvalue().strip()
        lines = output.split('\n')

        self.assertEqual(lines[0], 'fabrecipes/master ')
        self.assertEqual(lines[1], 'gitcheck/master ')
        self.assertEqual(lines[2], 'serialkiller/master')

if __name__ == "__main__":
    unittest.main(verbosity=2)
