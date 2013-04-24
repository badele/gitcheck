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

    gitstatus = gitExec(rep, "git status -suno | grep -v '??'"
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
    tcount = acount + mcount + dcount
    change = not (acount == 0 and mcount == 0 and dcount == 0)
    if not change:
        color = tcolor.DEFAULT + tcolor.GREEN
    else:
        color = tcolor.BOLD + tcolor.RED

    # Print result
    prjname = "%s%s%s" % (color, rep, tcolor.DEFAULT)
    if change:
        countstr = "%sLocal%s[" % (tcolor.ORANGE, tcolor.DEFAULT)
        if tcount > 0:
            countstr += "%sTo commit:%s%s" % (
                tcolor.BLUE,
                tcolor.DEFAULT,
                len(getLocalFilesChange(rep))
            )

        # if mcount > 0:
        #     countstr += "%sModifify:%s%s" % (
        #         tcolor.BLUE,
        #         tcolor.DEFAULT,
        #         mcount
        #     )
        # if acount > 0:
        #     countstr += " / %sAdd:%s%s" % (
        #         tcolor.BLUE,
        #         tcolor.DEFAULT,
        #         acount
        #     )
        # if dcount > 0:
        #     countstr += " / %sDelete:%s%s" % (
        #         tcolor.BLUE,
        #         tcolor.DEFAULT,
        #         dcount
        #     )
        countstr += "]"
    else:
        countstr = ""

    branch = getDefaultBranch(rep)
    if branch != "":
        remotes = getRemoteRepositories(rep)
        for r in remotes:
            count = len(getLocalToPush(rep, r, branch))
            if count > 0:
                countstr += " %s%s%s[%sTo Push:%s%s]" % (
                    tcolor.ORANGE,
                    r,
                    tcolor.DEFAULT,
                    tcolor.BLUE,
                    tcolor.DEFAULT,
                    count
                )

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


def getLocalFilesChange(rep):
    files = []
    curdir = os.path.abspath(os.getcwd())
    snbchange = re.compile(r'^(.{2}) (.*)')
    result = gitExec(rep, "git status -suno"
                     % locals())

    lines = result.split('\n')
    for l in lines:
        m = snbchange.match(l)
        if m:
            files.append([m.group(1), m.group(2)])

    return files


def getLocalToPush(rep, remote, branch):
    result = gitExec(rep, "git log %(remote)s/%(branch)s..HEAD --oneline"
                     % locals())

    return [x for x in result.split('\n') if x]


# Get Default branch for repository
def getDefaultBranch(rep):
    curdir = os.path.abspath(os.getcwd())
    sbranch = re.compile(r'^\* (.*)')
    gitbranch = gitExec(rep, "git branch | grep '*'"
                        % locals())

    branch = ""
    m = sbranch.match(gitbranch)
    if m:
        branch = m.group(1)

    return branch


def getRemoteRepositories(rep):
    result = gitExec(rep, "git remote"
                     % locals())

    remotes = [x for x in result.split('\n') if x]
    return remotes


# Custom git command
def gitExec(rep, command):
    curdir = os.path.abspath(os.getcwd())
    cmd = "cd %(curdir)s/%(rep)s ; %(command)s" % locals()

    cmd = os.popen(cmd)
    return cmd.read()


# Check all git repositories
def gitcheck(verbose):
    repo = searchRepositories()
    for r in repo:
        checkRepository(r, verbose)


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
