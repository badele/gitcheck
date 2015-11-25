#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import os
import re
import sys
import getopt
import time
import subprocess
from subprocess import PIPE
import smtplib
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import shlex

from os.path import expanduser
from time import strftime

import json

from colored import fg, bg, attr

# Global vars
argopts = {}

#Load custom parameters from ~/mygitcheck.py
configfile = expanduser('~/mygitcheck.py')
if os.path.exists(configfile):
    sys.path.append(expanduser('~'))
    import mygitcheck as userconf

    # Try to load colorthemme
    if hasattr(userconf, 'colortheme'):
        colortheme = userconf.colortheme
    else:
        # Default theme
        defaultcolor = attr('reset') + fg('white')
        colortheme = {
            'default': defaultcolor,
            'prjchanged': attr('reset') + attr('bold') + fg('deep_pink_1a'),
            'prjremote': attr('reverse') + fg('light_cyan'),
            'prjname': attr('reset') + fg('chartreuse_1'),
            'reponame': attr('reset') + fg('light_goldenrod_2b'),
            'branchname': defaultcolor,
            'fileupdated': attr('reset') + fg('light_goldenrod_2b'),
            'remoteto': attr('reset') + fg('deep_sky_blue_3b'),
            'committo': attr('reset') + fg('violet'),
            'commitinfo': attr('reset') + fg('deep_sky_blue_3b'),
            'commitstate': attr('reset') + fg('deep_pink_1a'),
            'bell': "\a",
            'reset': "\033[2J\033[H"
        }


class html:
    msg = "<ul>\n"
    topull = ""
    topush = ""
    strlocal = ""
    prjname = ""
    path = ""
    timestamp = ""


def showDebug(mess, level='info'):
    if argopts.get('debugmod', False):
        print(mess)


# Search all local repositories from current directory
def searchRepositories():
    showDebug('Beginning scan... building list of git folders')
    dir = argopts.get('searchDir', None)
    if dir is not None and dir[-1:] == '/':
        dir = dir[:-1]
    curdir = os.path.abspath(os.getcwd()) if dir is None else dir
    showDebug("  Scan git repositories from %s" % curdir)

    html.path = curdir
    startinglevel = curdir.count(os.sep)
    repo = []

    for directory, dirnames, filenames in os.walk(curdir):
        level = directory.count(os.sep) - startinglevel
        if argopts.get('depth', None) is None or level <= argopts.get('depth', None):
            if '.git' in dirnames:
                showDebug("  Add %s repository" % directory)
                repo.append(directory)

    repo.sort()
    showDebug('Done')
    return repo


# Check state of a git repository
def checkRepository(rep, branch):
    aitem = []
    mitem = []
    ditem = []
    gsearch = re.compile(r'^.?([A-Z]) (.*)')

    if re.match(argopts.get('ignoreBranch', r'^$'), branch):
        return False

    changes = getLocalFilesChange(rep)
    ischange = len(changes) > 0
    actionNeeded = False  # actionNeeded is branch push/pull, not local file change.

    topush = ""
    topull = ""
    html.topush = ""
    html.topull = ""
    if branch != "":
        remotes = getRemoteRepositories(rep)
        hasremotes = bool(remotes)
        for r in remotes:
            count = len(getLocalToPush(rep, r, branch))
            ischange = ischange or (count > 0)
            actionNeeded = actionNeeded or (count > 0)
            if count > 0:
                topush += " %s%s%s[%sTo Push:%s%s]" % (
                    colortheme['reponame'],
                    r,
                    colortheme['default'],
                    colortheme['remoteto'],
                    colortheme['default'],
                    count
                )
                html.topush += '<b style="color:black">%s</b>[<b style="color:blue">To Push:</b><b style="color:black">%s</b>]' % (
                    r,
                    count
                )

        for r in remotes:
            count = len(getRemoteToPull(rep, r, branch))
            ischange = ischange or (count > 0)
            actionNeeded = actionNeeded or (count > 0)
            if count > 0:
                topull += " %s%s%s[%sTo Pull:%s%s]" % (
                    colortheme['reponame'],
                    r,
                    colortheme['default'],
                    colortheme['remoteto'],
                    colortheme['default'],
                    count
                )
                html.topull += '<b style="color:black">%s</b>[<b style="color:blue">To Pull:</b><b style="color:black">%s</b>]' % (
                    r,
                    count
                )
    if ischange or not argopts.get('quiet', False):
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
            repname = rep[len(os.path.abspath(os.getcwd())) + 1:]
        # Case 3: script was started with -d and above cases do not apply
        else:
            repname = rep

        if ischange:
            prjname = "%s%s%s" % (colortheme['prjchanged'], repname, colortheme['default'])
            html.prjname = '<b style="color:red">%s</b>' % (repname)
        elif not hasremotes:
            prjname = "%s%s%s" % (colortheme['prjremote'], repname, colortheme['default'])
            html.prjname = '<b style="color:magenta">%s</b>' % (repname)
        else:
            prjname = "%s%s%s" % (colortheme['prjname'], repname, colortheme['default'])
            html.prjname = '<b style="color:green">%s</b>' % (repname)

        # Print result
        if len(changes) > 0:
            strlocal = "%sLocal%s[" % (colortheme['reponame'], colortheme['default'])
            lenFilesChnaged = len(getLocalFilesChange(rep))
            strlocal += "%sTo Commit:%s%s" % (
                colortheme['remoteto'],
                colortheme['default'],
                lenFilesChnaged
            )
            html.strlocal = '<b style="color:orange"> Local</b><b style="color:black">['
            html.strlocal += "To Commit:%s" % (
                lenFilesChnaged
            )
            strlocal += "]"
            html.strlocal += "]</b>"
        else:
            strlocal = ""
            html.strlocal = ""

        if argopts.get('email', False):
            html.msg += "<li>%s/%s %s %s %s</li>\n" % (html.prjname, branch, html.strlocal, html.topush, html.topull)

        else:
            cbranch = "%s%s" % (colortheme['branchname'], branch)
            print("%(prjname)s/%(cbranch)s %(strlocal)s%(topush)s%(topull)s" % locals())

        if argopts.get('verbose', False):
            if ischange > 0:
                filename = "  |--Local"
                if not argopts.get('email', False):
                    print(filename)
                html.msg += '<ul><li><b>Local</b></li></ul>\n<ul>\n'
                for c in changes:
                    filename = "     |--%s%s%s %s%s" % (
                        colortheme['commitstate'],
                        c[0],
                        colortheme['fileupdated'],
                        c[1],
                        colortheme['default'])
                    html.msg += '<li> <b style="color:orange">[To Commit] </b>%s</li>\n' % c[1]
                    if not argopts.get('email', False): print(filename)
                html.msg += '</ul>\n'
            if branch != "":
                remotes = getRemoteRepositories(rep)
                for r in remotes:
                    commits = getLocalToPush(rep, r, branch)
                    if len(commits) > 0:
                        rname = "  |--%(r)s" % locals()
                        html.msg += '<ul><li><b>%(r)s</b></li>\n</ul>\n<ul>\n' % locals()
                        if not argopts.get('email', False): print(rname)
                        for commit in commits:
                            pcommit = "     |--%s[To Push]%s %s%s%s" % (
                                colortheme['committo'],
                                colortheme['default'],
                                colortheme['commitinfo'],
                                commit,
                                colortheme['default'])
                            html.msg += '<li><b style="color:blue">[To Push] </b>%s</li>\n' % commit
                            if not argopts.get('email', False): print(pcommit)
                        html.msg += '</ul>\n'

            if branch != "":
                remotes = getRemoteRepositories(rep)
                for r in remotes:
                    commits = getRemoteToPull(rep, r, branch)
                    if len(commits) > 0:
                        rname = "  |--%(r)s" % locals()
                        html.msg += '<ul><li><b>%(r)s</b></li>\n</ul>\n<ul>\n' % locals()
                        if not argopts.get('email', False): print(rname)
                        for commit in commits:
                            pcommit = "     |--%s[To Pull]%s %s%s%s" % (
                                colortheme['committo'],
                                colortheme['default'],
                                colortheme['commitinfo'],
                                commit,
                                colortheme['default'])
                            html.msg += '<li><b style="color:blue">[To Pull] </b>%s</li>\n' % commit
                            if not argopts.get('email', False): print(pcommit)
                        html.msg += '</ul>\n'

    return actionNeeded


def getLocalFilesChange(rep):
    files = []
    #curdir = os.path.abspath(os.getcwd())
    snbchange = re.compile(r'^(.{2}) (.*)')
    onlyTrackedArg = "" if argopts.get('checkUntracked', False) else "uno"
    result = gitExec(rep, "status -s" + onlyTrackedArg)

    lines = result.split('\n')
    for l in lines:
        if not re.match(argopts.get('ignoreLocal', r'^$'), l):
            m = snbchange.match(l)
            if m:
                files.append([m.group(1), m.group(2)])

    return files


def hasRemoteBranch(rep, remote, branch):
    result = gitExec(rep, 'branch -r')
    return '%s/%s' % (remote, branch) in result


def getLocalToPush(rep, remote, branch):
    if not hasRemoteBranch(rep, remote, branch):
        return []
    result = gitExec(rep, "log %(remote)s/%(branch)s..%(branch)s --oneline"
                     % locals())

    return [x for x in result.split('\n') if x]


def getRemoteToPull(rep, remote, branch):
    if not hasRemoteBranch(rep, remote, branch):
        return []
    result = gitExec(rep, "log %(branch)s..%(remote)s/%(branch)s --oneline"
                     % locals())

    return [x for x in result.split('\n') if x]


def updateRemote(rep):
    gitExec(rep, "remote update")


# Get Default branch for repository
def getDefaultBranch(rep):
    sbranch = re.compile(r'^\* (.*)', flags=re.MULTILINE)
    gitbranch = gitExec(rep, "branch"
                        % locals())

    branch = ""
    m = sbranch.search(gitbranch)
    if m:
        branch = m.group(1)

    return {branch}


# Get all branches for repository
def getAllBranches(rep):
    gitbranch = gitExec(rep, "branch"
                        % locals())

    branch = gitbranch.splitlines()

    return [b[2:] for b in branch]


def getRemoteRepositories(rep):
    result = gitExec(rep, "remote"
                     % locals())

    remotes = [x for x in result.split('\n') if x]
    return remotes


def gitExec(path, cmd):
    commandToExecute = "git -C \"%s\" %s" % (path, cmd)
    cmdargs = shlex.split(commandToExecute)
    showDebug("EXECUTE GIT COMMAND '%s'" % cmdargs)
    p = subprocess.Popen(cmdargs, stdout=PIPE, stderr=PIPE)
    output, errors = p.communicate()
    if p.returncode:
        print('Failed running %s' % commandToExecute)
        raise Exception(errors)
    return output.decode('utf-8')


# Check all git repositories
def gitcheck():
    showDebug("Global Vars: %s" % argopts)

    repo = searchRepositories()
    actionNeeded = False

    if argopts.get('checkremote', False):
        for r in repo:
            print ("Updating %s remotes..." % r)
            updateRemote(r)

    if argopts.get('watchInterval', 0) > 0:
        print(colortheme['reset'])
        print(strftime("%Y-%m-%d %H:%M:%S"))

    showDebug("Processing repositories... please wait.")
    for r in repo:
        if (argopts.get('checkall', False)):
            branch = getAllBranches(r)
        else:
            branch = getDefaultBranch(r)
        for b in branch:
            if checkRepository(r, b):
                actionNeeded = True
    html.timestamp = strftime("%Y-%m-%d %H:%M:%S")
    html.msg += "</ul>\n<p>Report created on %s</p>\n" % html.timestamp

    if actionNeeded and argopts.get('bellOnActionNeeded', False):
        print(colortheme['bell'])


def sendReport(content):
    userPath = expanduser('~')
    filepath = r'%s\Documents\.gitcheck' % userPath
    filename = filepath + "//mail.properties"
    config = json.load(open(filename))

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Gitcheck Report (%s)" % (html.path)
    msg['From'] = config['from']
    msg['To'] = config['to']

    # Create the body of the message (a plain-text and an HTML version).
    text = "Gitcheck report for %s created on %s\n\n This file can be seen in html only." % (html.path, html.timestamp)
    htmlcontent = "<html>\n<head>\n<h1>Gitcheck Report</h1>\n<h2>%s</h2>\n</head>\n<body>\n<p>%s</p>\n</body>\n</html>" % (
        html.path, content
    )
    # Write html file to disk
    f = open(filepath + '//result.html', 'w')
    f.write(htmlcontent)
    print ("File saved under %s\\result.html" % filepath)
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(htmlcontent, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    try:
        print ("Sending email to %s" % config['to'])
        # Send the message via local SMTP server.
        s = smtplib.SMTP(config['smtp'], config['smtp_port'])
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(config['from'], config['to'], msg.as_string())
        s.quit()
    except SMTPException as e:
        print("Error sending email : %s" % str(e))


def initEmailConfig():

    config = {
        'smtp': 'yourserver',
        'smtp_port': 25,
        'from': 'from@server.com',
        'to': 'to@server.com'
    }
    userPath = expanduser('~')
    saveFilePath = r'%s\Documents\.gitcheck' % userPath
    if not os.path.exists(saveFilePath):
        os.makedirs(saveFilePath)
    filename = saveFilePath + '\mail.properties'
    json.dump(config, fp=open(filename, 'w'), indent=4)
    print('Please, modify config file located here : %s' % filename)


def readDefaultConfig():
    filename = expanduser('~/.gitcheck')
    if os.path.exists(filename):
        pass


def usage():
    print("Usage: %s [OPTIONS]" % (sys.argv[0]))
    print("Check multiple git repository in one pass")
    print("== Common options ==")
    print("  -v, --verbose                        Show files & commits")
    print("  --debug                              Show debug message")
    print("  -r, --remote                         force remote update (slow)")
    print("  -u, --untracked                      Show untracked files")
    print("  -b, --bell                           bell on action needed")
    print("  -w <sec>, --watch=<sec>              after displaying, wait <sec> and run again")
    print("  -i <re>, --ignore-branch=<re>        ignore branches matching the regex <re>")
    print("  -d <dir>, --dir=<dir>                Search <dir> for repositories")
    print("  -m <maxdepth>, --maxdepth=<maxdepth> Limit the depth of repositories search")
    print("  -q, --quiet                          Display info only when repository needs action")
    print("  -e, --email                          Send an email with result as html, using mail.properties parameters")
    print("  -a, --all-branch                     Show the status of all branches")
    print("  -l <re>, --localignore=<re>          ignore changes in local files which match the regex <re>")
    print("  --init-email                         Initialize mail.properties file (has to be modified by user using JSON Format)")


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "vhrubw:i:d:m:q:e:al:",
            [
                "verbose", "debug", "help", "remote", "untracked", "bell", "watch=", "ignore-branch=",
                "dir=", "maxdepth=", "quiet", "email", "init-email", "all-branch", "localignore="
            ]
        )
    except getopt.GetoptError as e:
        if e.opt == 'w' and 'requires argument' in e.msg:
            print("Please indicate nb seconds for refresh ex: gitcheck -w10")
        else:
            print(e.msg)
        sys.exit(2)

    readDefaultConfig()
    for opt, arg in opts:
        if opt in ["-v", "--verbose"]:
            argopts['verbose'] = True
        elif opt in ["--debug"]:
            argopts['debugmod'] = True
        elif opt in ["-r", "--remote"]:
            argopts['checkremote'] = True
        elif opt in ["-u", "--untracked"]:
            argopts['checkUntracked'] = True
        elif opt in ["-b", "--bell"]:
            argopts['bellOnActionNeeded'] = True
        elif opt in ["-w", "--watch"]:
            try:
                argopts['watchInterval'] = float(arg)
            except ValueError:
                print("option %s requires numeric value" % opt)
                sys.exit(2)
        elif opt in ["-i", "--ignore-branch"]:
            argopts['ignoreBranch'] = arg
        elif opt in ["-l", "--localignore"]:
            argopts['ignoreLocal'] = arg
        elif opt in ["-d", "--dir"]:
            argopts['searchDir'] = arg
        elif opt in ["-m", '--maxdepth']:
            try:
                argopts['depth'] = int(arg)
            except ValueError:
                print("option %s requires int value" % opt)
                sys.exit(2)
        elif opt in ["-q", "--quiet"]:
            argopts['quiet'] = True
        elif opt in ["-e", "--email"]:
            argopts['email'] = True
        elif opt in ["-a", "--all-branch"]:
            argopts['checkall'] = True
        elif opt in ["--init-email"]:
            initEmailConfig()
            sys.exit(0)
        elif opt in ["-h", "--help"]:
            usage()
            sys.exit(0)
#        else:
#            print "Unhandled option %s" % opt
#            sys.exit(2)

    while True:
        try:
            gitcheck()

            if argopts.get('email', False):
                sendReport(html.msg)

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print ("Unexpected error:", str(e))

        if argopts.get('watchInterval', 0) > 0:
            time.sleep(argopts.get('watchInterval', 0))
        else:
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
