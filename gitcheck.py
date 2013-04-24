#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import getopt
import fnmatch


# Class for terminal Color
class tcolor:
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[96m"
    ORANGE = "\033[93m"


# Search all repositories from current directory
def searchRepositories():
    curdir = os.path.abspath(os.getcwd())

    repo = []
    rsearch = re.compile(r'^/?(.*?)/\.git')
    for root, dirnames, filenames in os.walk(curdir):
        for dirnames in fnmatch.filter(dirnames, '*.git'):
            fdir = os.path.join(root, dirnames)
            fdir = fdir.replace(curdir, '')
            m = rsearch.match(fdir)
            if m:
                repo.append(m.group(1))

    return repo


# Check state of a git repository
def checkRepository(rep, verbose=False):
    aitem = []
    mitem = []
    ditem = []
    curdir = os.path.abspath(os.getcwd())
    gsearch = re.compile(r'^.?([A-Z]) (.*)')

    gitstatus = sysexec("cd %(curdir)s/%(rep)s ; git status -s | grep -v '??'"
                        % locals())
    branch = getDefaultBranch(rep)

    # Analyse git status log
    lines = gitstatus.split('\n')
    for l in lines:
        m = gsearch.match(l)
        if m:
            state = m.group(1)
            if state == 'M':
                mitem.append(m.group(2))
            if state == 'A':
                aitem.append(m.group(2))
            if state == 'D':
                ditem.append(m.group(2))

    # Check if they have modifications
    acount = len(aitem)
    mcount = len(mitem)
    dcount = len(ditem)
    change = not (acount == 0 and mcount == 0 and dcount == 0)
    if not change:
        color = tcolor.DEFAULT + tcolor.GREEN
    else:
        color = tcolor.BOLD + tcolor.RED

    # Print result
    prjname = "%s%s%s" % (color, rep, tcolor.DEFAULT)
    if change:
        countstr = "%sLocal%s[" % (tcolor.ORANGE, tcolor.DEFAULT)
        if mcount > 0:
            countstr += "%sModifify:%s%s" % (
                tcolor.BLUE,
                tcolor.DEFAULT,
                mcount
            )
        if acount > 0:
            countstr += " / %sAdd:%s%s" % (
                tcolor.BLUE,
                tcolor.DEFAULT,
                acount
            )
        if dcount > 0:
            countstr += " / %sDelete:%s%s" % (
                tcolor.BLUE,
                tcolor.DEFAULT,
                dcount
            )
        countstr += "]"
    else:
        countstr = ""

    print("%(prjname)s/%(branch)s %(countstr)s" % locals())

    if verbose:
        for m in mitem:
            filename = "  |--%s%s%s" % (tcolor.ORANGE, m, tcolor.DEFAULT)
            print(filename)
        for a in aitem:
            filename = "  |--%s%s%s(+)" % (tcolor.ORANGE, a, tcolor.DEFAULT)
            print(filename)
        for d in ditem:
            filename = "  |--%s%s%s(-)" % (tcolor.ORANGE, d, tcolor.DEFAULT)
            print(filename)


# Get Default branch for repository
def getDefaultBranch(rep):
    curdir = os.path.abspath(os.getcwd())
    sbranch = re.compile(r'^\* (.*)')
    gitbranch = sysexec("cd %(curdir)s/%(rep)s ; git branch | grep '*'"
                        % locals())

    branch = ""
    m = sbranch.match(gitbranch)
    if m:
        branch = m.group(1)

    return branch


# Check all git repositories
def gitcheck(verbose):
    repo = searchRepositories()
    for r in repo:
        checkRepository(r, verbose)


def sysexec(cmdLine):
    cmd = os.popen(cmdLine)
    return cmd.read()


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "v",
            ["verbose", ])
    except getopt.GetoptError:
        sys.exit(2)

    verbose = False
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True

    gitcheck(verbose)

if __name__ == "__main__":
    main()
