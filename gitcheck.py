#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import getopt
import fnmatch
import time
import subprocess
from subprocess import PIPE, call, Popen

# Class for terminal Color
class tcolor:
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[0;1;31;40m"
    GREEN = "\033[0;1;32;40m"
    BLUE = "\033[1;34;4;47m"
    ORANGE = "\033[1;33;4;41m"
    MAGENTA = "\033[0;1;36;40m"
    RESET = "\033[2J\033[H"
    BELL = "\a"

# Search all local repositories from current directory
#def searchRepositories(dir=None, depth=None):
#
#    # if trailing slash is in argument of option -d, it won't work -> get rid of it
#    if dir != None and dir[-1:] == '/':
#        dir = dir[:-1]
#    curdir = os.path.abspath(os.getcwd()) if dir is None else dir
#    startinglevel = curdir.count(os.sep)
#    repo = []
#    rsearch = re.compile(r'^/?(.*?)/\.git')
#    for root, dirnames, filenames in os.walk(curdir, followlinks=True):
#        level = root.count(os.sep) - startinglevel
#        if depth == None or level <= depth:
#            for dirnames in fnmatch.filter(dirnames, '*.git'):
#                fdir = os.path.join(root, dirnames)
#                fdir = fdir.replace(curdir, '')
#                m = rsearch.match(fdir)
#                if m:
#                    repo.append(os.path.join(curdir, m.group(1)))
#
#    return repo

def searchRepositories(dir=None, depth=None): 

    if dir != None and dir[-1:] == '/':
        dir = dir[:-1]
    curdir = os.path.abspath(os.getcwd()) if dir is None else dir
    startinglevel = curdir.count(os.sep)
    repo = []

    def step(ext, dirname, names):
        ext = ext.lower()
        for name in names:
            if name.lower().endswith(ext):
                repo.append(os.path.join(dirname, name)[:-5])
                #print '%s' % (os.path.join(dirname, name))[:-5]

    def is_git_directory(path = '.'):
        return subprocess.call(['git', '-C', path, 'status'], stderr=subprocess.STDOUT, stdout = open(os.devnull, 'w')) == 0

    # Start the walk
    #print "Walking the path..."
    os.path.walk(curdir, step, '.git')
    return repo

# Check state of a git repository
def checkRepository(rep, verbose=False, ignoreBranch=r'^$', quiet=False):
    aitem = []
    mitem = []
    ditem = []
    gsearch = re.compile(r'^.?([A-Z]) (.*)')

    branch = getDefaultBranch(rep)
    if re.match(ignoreBranch, branch):
        return False

    changes = getLocalFilesChange(rep)
    ischange = len(changes) > 0
    actionNeeded = False # actionNeeded is branch push/pull, not local file change.

    branch = getDefaultBranch(rep)
    topush = ""
    topull = ""
    if branch != "":
        remotes = getRemoteRepositories(rep)
        for r in remotes:
            count = len(getLocalToPush(rep, r, branch))
            ischange = ischange or (count > 0)
            actionNeeded = actionNeeded or (count > 0)
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
            actionNeeded = actionNeeded or (count > 0)
            if count > 0:
                topull += " %s%s%s[%sTo Pull:%s%s]" % (
                    tcolor.ORANGE,
                    r,
                    tcolor.DEFAULT,
                    tcolor.BLUE,
                    tcolor.DEFAULT,
                    count
                )
    if ischange or not quiet:
        if ischange:
            color = tcolor.BOLD + tcolor.RED
        else:
            color = tcolor.DEFAULT + tcolor.GREEN

        # Remove trailing slash from repository/directory name
        if rep[-1:] == '/':
            rep = rep[:-1]

        # Do some magic to not show the absolute path as repository name
        # Case 1: script was started in a directory that is a git repo
        if rep == os.path.abspath(os.getcwd()):
            (head, tail) = os.path.split(rep)
            if tail != '':
                repname = tail
        # Case 2: script was started in a directory with possible subdirs that contain git repos
        elif rep.find(os.path.abspath(os.getcwd())) == 0:
            repname = rep[len(os.path.abspath(os.getcwd()))+1:]
        # Case 3: script was started with -d and above cases do not apply
        else:
            repname = rep

        # Print result
        prjname = "%s%s%s" % (color, repname, tcolor.DEFAULT)
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

    return actionNeeded

def getLocalFilesChange(rep):
    files = []
    #curdir = os.path.abspath(os.getcwd())
    snbchange = re.compile(r'^(.{2}) (.*)')
    result = gitExec(rep, "status -suno")

    lines = result.split('\n')
    for l in lines:
        m = snbchange.match(l)
        if m:
            files.append([m.group(1), m.group(2)])

    return files


def hasRemoteBranch(rep, remote, branch):
    #result = gitExec(rep, 'branch -r | grep "%s/%s"' % (remote,branch))
    #return (result != "")
	return True


def getLocalToPush(rep, remote, branch):
    if not hasRemoteBranch(rep, remote, branch):
        return []
    result = gitExec(rep, "log %(remote)s/%(branch)s..HEAD --oneline"
                     % locals())

    return [x for x in result.split('\n') if x]


def getRemoteToPull(rep, remote, branch):
    if not hasRemoteBranch(rep, remote, branch):
        return []
    result = gitExec(rep, "log HEAD..%(remote)s/%(branch)s --oneline"
                     % locals())

    return [x for x in result.split('\n') if x]


def updateRemote(rep):
    gitExec(rep, "remote update")


# Get Default branch for repository
def getDefaultBranch(rep):
    sbranch = re.compile(r'^\* (.*)')
    gitbranch = gitExec(rep, "branch"
                        % locals())

    branch = ""
    m = sbranch.match(gitbranch)
    if m:
        branch = m.group(1)

    return branch

#git -C "c:\0Programmes\Librairies\gitcheck" branch -r | grep 'origin/master'
def getRemoteRepositories(rep):
    result = gitExec(rep, "remote"
                     % locals())

    remotes = [x for x in result.split('\n') if x]
    return remotes


# Custom git command
#def gitExec(rep, command):
#    cmd = "cd \"%(rep)s\" ; %(command)s" % locals()
#    cmd = os.popen(cmd)
#    return cmd.read()

def gitExec(path,cmd):
    commandToExecute = "git -C \"%s\" %s" % (path,cmd)
    #print "%s" % commandToExecute 
    p = subprocess.Popen(commandToExecute, stdout=PIPE, stderr=PIPE, bufsize=256*1024*1024)
    output, errors = p.communicate()
    if p.returncode:
        raise Exception(errors)
    else:
        # Print stdout from cmd call
        #print "%s" % output
        pass
    return output

# Check all git repositories
def gitcheck(verbose, checkremote, ignoreBranch, bellOnActionNeeded, shouldClear, searchDir, depth, quiet):
    repo = searchRepositories(searchDir, depth)
    actionNeeded = False

    if checkremote:
        print ("Please wait, refreshing data of remote repositories...")
        for r in repo:
            updateRemote(r)

    if shouldClear:
        print(tcolor.RESET)

    for r in repo:
        if checkRepository(r, verbose, ignoreBranch, quiet):
            actionNeeded = True

    if actionNeeded and bellOnActionNeeded:
        print(tcolor.BELL)


def usage():
    print("Usage: %s [OPTIONS]" % (sys.argv[0]))
    print("Check multiple git repository in one pass")
    print("== Common options ==")
    print("  -v, --verbose                        Show files & commits")
    print("  -r, --remote                         force remote update(slow)")
    print("  -b, --bell                           bell on action needed")
    print("  -w <sec>, --watch=<sec>              after displaying, wait <sec> and run again")
    print("  -i <re>, --ignore-branch=<re>        ignore branches matching the regex <re>")
    print("  -d <dir>, --dir=<dir>                Search <dir> for repositories")
    print("  -m <maxdepth>, --maxdepth=<maxdepth> Limit the depth of repositories search")
    print("  -q, --quiet                          Display info only when repository needs action")

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "vhrbw:i:d:m:q",
            ["verbose", "help", "remote", "bell", "watch=", "ignore-branch=",
             "dir=", "maxdepth=", "quiet"])
    except getopt.GetoptError, e:
        if e.opt == 'w' and 'requires argument' in e.msg:
            print "Please indicate nb seconds for refresh ex: gitcheck -w10"
        else:
            print e.msg
        sys.exit(2)

    verbose = False
    checkremote = False
    watchInterval = 0
    bellOnActionNeeded = False
    searchDir = None
    depth = None
    quiet = False
    ignoreBranch = r'^$'  # empty string
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-r", "--remote"):
            checkremote = True
        elif opt in ("-r", "--remote"):
            checkremote = True
        elif opt in ("-b", "--bell"):
            bellOnActionNeeded = True
        elif opt in ("-w", "--watch"):
            try:
                watchInterval = float(arg)
            except ValueError:
                print "option %s requires numeric value" % opt
                sys.exit(2)
        elif opt in ("-i", "--ignore-branch"):
            ignoreBranch = arg
        elif opt in ("-d", "--dir"):
            searchDir = arg
        elif opt in ("-m", '--maxdepth'):
            try:
                depth = int(arg)
            except ValueError:
                print "option %s requires int value" % opt
                sys.exit(2)
        elif opt in ("-q", "--quiet"):
            quiet = True
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)
#        else:
#            print "Unhandled option %s" % opt
#            sys.exit(2)

    while True:
        gitcheck(
            verbose,
            checkremote,
            ignoreBranch,
            bellOnActionNeeded,
            watchInterval > 0,
            searchDir,
            depth,
            quiet
        )
        if watchInterval:
            time.sleep(watchInterval)
        else:
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
