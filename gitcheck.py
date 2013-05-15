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
    MAGENTA = "\033[95m"


# Search all local repositories from current directory
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
def checkRepository(rep, verbose=False, checkremote=False):
    aitem = []
    mitem = []
    ditem = []
    curdir = os.path.abspath(os.getcwd())
    gsearch = re.compile(r'^.?([A-Z]) (.*)')

    if checkremote:
        updateRemote(rep)

    branch = getDefaultBranch(rep)
    changes = getLocalFilesChange(rep)
    ischange = len(changes) > 0

    branch = getDefaultBranch(rep)
    topush = ""
    topull = ""
    if branch != "":
        remotes = getRemoteRepositories(rep)
        for r in remotes:
            count = len(getLocalToPush(rep, r, branch))
            ischange = ischange or (count > 0)
            if count > 0:
                topush += " %s%s%s[%sTo Push:%s%s]" % (
                    tcolor.ORANGE,
                    r,
                    tcolor.DEFAULT,
                    tcolor.BLUE,
                    tcolor.DEFAULT,
                    count
                )

        for r in remotes:
            count = len(getRemoteToPull(rep, r, branch))
            ischange = ischange or (count > 0)
            if count > 0:
                topull += " %s%s%s[%sTo Pull:%s%s]" % (
                    tcolor.ORANGE,
                    r,
                    tcolor.DEFAULT,
                    tcolor.BLUE,
                    tcolor.DEFAULT,
                    count
                )

    if ischange:
        color = tcolor.BOLD + tcolor.RED
    else:
        color = tcolor.DEFAULT + tcolor.GREEN

    # Print result
    prjname = "%s%s%s" % (color, rep, tcolor.DEFAULT)
    if len(changes) > 0:
        strlocal = "%sLocal%s[" % (tcolor.ORANGE, tcolor.DEFAULT)
        strlocal += "%sTo Commit:%s%s" % (
            tcolor.BLUE,
            tcolor.DEFAULT,
            len(getLocalFilesChange(rep))
        )

        strlocal += "]"
    else:
        strlocal = ""

    print("%(prjname)s/%(branch)s %(strlocal)s%(topush)s%(topull)s" % locals())
    if verbose:
        if ischange > 0:
            filename = "  |--Local"
            print(filename)
            for c in changes:
                filename = "     |--%s%s%s" % (
                    tcolor.ORANGE,
                    c[1],
                    tcolor.DEFAULT)
                print(filename)

        if branch != "":
            remotes = getRemoteRepositories(rep)
            for r in remotes:
                commits = getLocalToPush(rep, r, branch)
                if len(commits) > 0:
                    rname = "  |--%(r)s" % locals()
                    print(rname)
                    for commit in commits:
                        commit = "     |--%s[To Push]%s %s%s%s" % (
                            tcolor.MAGENTA,
                            tcolor.DEFAULT,
                            tcolor.BLUE,
                            commit,
                            tcolor.DEFAULT)
                        print(commit)

        if branch != "":
            remotes = getRemoteRepositories(rep)
            for r in remotes:
                commits = getRemoteToPull(rep, r, branch)
                if len(commits) > 0:
                    rname = "  |--%(r)s" % locals()
                    print(rname)
                    for commit in commits:
                        commit = "     |--%s[To Pull]%s %s%s%s" % (
                            tcolor.MAGENTA,
                            tcolor.DEFAULT,
                            tcolor.BLUE,
                            commit,
                            tcolor.DEFAULT)
                        print(commit)


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


def getRemoteToPull(rep, remote, branch):
    result = gitExec(rep, "git log HEAD..%(remote)s/%(branch)s --oneline"
                     % locals())

    return [x for x in result.split('\n') if x]


def updateRemote(rep):
    gitExec(rep, "git remote update")


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
def gitcheck(verbose, checkremote):
    repo = searchRepositories()
    for r in repo:
        checkRepository(r, verbose, checkremote)


def usage():
    print("Usage: %s [OPTIONS]" % (sys.argv[0]))
    print("Check multiple git repository in one pass")
    print("== Common options ==")
    print("  -v, --verbose                 Show files & commits")
    print("  -r, --remote                  force remote update(slow)")


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "vhr",
            ["verbose", "help", "remote", ])
    except getopt.GetoptError:
        sys.exit(2)

    verbose = False
    checkremote = False
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        if opt in ("-r", "--remote"):
            checkremote = True

        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

    gitcheck(verbose, checkremote)

if __name__ == "__main__":
    main()
