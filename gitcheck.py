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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import shlex

from configobj import ConfigObj
from os.path import expanduser
import os
from time import strftime


# Class for terminal Color
class tcolor:
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[0;1;31;40m"
    GREEN = "\033[0;1;32;40m"
    BLUE = "\033[0;1;36;40m"
    ORANGE = "\033[0;1;33;40m"
    MAGENTA = "\033[0;1;36;40m"
    RESET = "\033[2J\033[H"
    BELL = "\a"

class html:
    msg = "<ul>\n"
    topull = ""
    topush = ""
    strlocal = ""
    prjname = ""
    path = ""
    timestamp = ""
    
    
# Search all local repositories from current directory
def searchRepositories(dir=None, depth=None): 
    print 'Beginning scan... building list of git folders'
    if dir != None and dir[-1:] == '/':
        dir = dir[:-1]
    curdir = os.path.abspath(os.getcwd()) if dir is None else dir
    html.path = curdir
    startinglevel = curdir.count(os.sep)
    repo = []

    for directory, dirnames, filenames in os.walk(curdir):
        level = directory.count(os.sep) - startinglevel        
        if depth == None or level <= depth:          
            for d in dirnames:
                if d.endswith('.git'):  
                    repo.append(os.path.join(directory, d)[:-5])
    
    print 'Done'
    return repo

# Check state of a git repository
def checkRepository(rep, verbose=False, ignoreBranch=r'^$', quiet=False, email=False):
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
    html.topush = ""
    html.topull = ""
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
                    tcolor.ORANGE,
                    r,
                    tcolor.DEFAULT,
                    tcolor.BLUE,
                    tcolor.DEFAULT,
                    count
                )
                html.topull += '<b style="color:black">%s</b>[<b style="color:blue">To Pull:</b><b style="color:black">%s</b>]' % (
                    r,
                    count
                )
    if ischange or not quiet:
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

        if ischange:
            color = tcolor.BOLD + tcolor.RED
            html.prjname = '<b style="color:red">%s</b>' % (repname)
        else:
            color = tcolor.DEFAULT + tcolor.GREEN
            html.prjname = '<b style="color:green">%s</b>' % (repname)

        # Print result
        prjname = "%s%s%s" % (color, repname, tcolor.DEFAULT)
        
        if len(changes) > 0:
            strlocal = "%sLocal%s[" % (tcolor.ORANGE, tcolor.DEFAULT)
            strlocal += "%sTo Commit:%s%s" % (
                tcolor.BLUE,
                tcolor.DEFAULT,
                len(getLocalFilesChange(rep))
            )
            html.strlocal = '<b style="color:orange"> Local</b><b style="color:black">['
            html.strlocal += "To Commit:%s" % (
                len(getLocalFilesChange(rep))
            )
            strlocal += "]"
            html.strlocal += "]</b>"
        else:
            strlocal = ""
            html.strlocal = ""
        
        if email:
            html.msg += "<li>%s/%s %s %s %s</li>\n" % (html.prjname, branch, html.strlocal, html.topush, html.topull)        
            
        else:
            print("%(prjname)s/%(branch)s %(strlocal)s%(topush)s%(topull)s" % locals())
               
        if verbose:
            if ischange > 0:
                filename = "  |--Local"
                if not email: print(filename)
                html.msg += '<ul><li><b>Local</b></li></ul>\n<ul>\n'                     
                for c in changes:
                    filename = "     |--%s%s%s" % (
                        tcolor.ORANGE,
                        c[1],
                        tcolor.DEFAULT)
                    html.msg += '<li> <b style="color:orange">[To Commit] </b>%s</li>\n' % c[1]
                    if not email:print(filename)
                html.msg += '</ul>\n'
            if branch != "":
                remotes = getRemoteRepositories(rep)
                for r in remotes:
                    commits = getLocalToPush(rep, r, branch)
                    if len(commits) > 0:
                        rname = "  |--%(r)s" % locals()
                        html.msg += '<ul><li><b>%(r)s</b></li>\n</ul>\n<ul>\n' % locals()
                        if not email:print(rname)
                        for commit in commits:
                            pcommit = "     |--%s[To Push]%s %s%s%s" % (
                                tcolor.MAGENTA,
                                tcolor.DEFAULT,
                                tcolor.BLUE,
                                commit,
                                tcolor.DEFAULT)
                            html.msg += '<li><b style="color:blue">[To Push] </b>%s</li>\n' % commit
                            if not email:print(pcommit)
                        html.msg += '</ul>\n'

            if branch != "":
                remotes = getRemoteRepositories(rep)
                for r in remotes:
                    commits = getRemoteToPull(rep, r, branch)
                    if len(commits) > 0:
                        rname = "  |--%(r)s" % locals()
                        html.msg += '<ul><li><b>%(r)s</b></li>\n</ul>\n<ul>\n' % locals()
                        if not email:print(rname)
                        for commit in commits:
                            pcommit = "     |--%s[To Pull]%s %s%s%s" % (
                                tcolor.MAGENTA,
                                tcolor.DEFAULT,
                                tcolor.BLUE,
                                commit,
                                tcolor.DEFAULT)
                            html.msg += '<li><b style="color:blue">[To Pull] </b>%s</li>\n' % commit
                            if not email:print(pcommit)
                        html.msg += '</ul>\n'

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
    result = gitExec(rep, 'branch -r')
    return '%s/%s'% (remote,branch) in result


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

def getRemoteRepositories(rep):
    result = gitExec(rep, "remote"
                     % locals())

    remotes = [x for x in result.split('\n') if x]
    return remotes


def gitExec(path,cmd):
    commandToExecute = "git -C \"%s\" %s" % (path, cmd)
    cmdargs = shlex.split(commandToExecute)
    p = subprocess.Popen(cmdargs, stdout=PIPE, stderr=PIPE)
    output, errors = p.communicate()
    if p.returncode:
        print 'Failed running %s' % commandToExecute
        raise Exception(errors)
    else:
        pass
    return output


# Check all git repositories
def gitcheck(verbose, checkremote, ignoreBranch, bellOnActionNeeded, shouldClear, searchDir, depth, quiet, email):
    repo = searchRepositories(searchDir, depth)
    actionNeeded = False

    if checkremote:
        print ("Please wait, refreshing data of remote repositories...")
        for r in repo:
            updateRemote(r)

    if shouldClear:
        print(tcolor.RESET)

    print ("Processing repositories... please wait.")
    for r in repo:
        if checkRepository(r, verbose, ignoreBranch, quiet, email):
            actionNeeded = True
    html.timestamp = strftime("%Y-%m-%d %H:%M:%S")                
    html.msg += "</ul>\n<p>Report created on %s</p>\n" % html.timestamp
    
    
    if actionNeeded and bellOnActionNeeded:
        print(tcolor.BELL)
    
    return True

def sendReport(content):
    userPath = expanduser('~')
    filepath = r'%s\Documents\.gitcheck' %(userPath)     
    filename = filepath + "//mail.properties"    
    config = ConfigObj(filename)    
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Gitcheck Report (%s)" % (html.path)
    msg['From'] = config['from']
    msg['To'] = config['to']
    
    # Create the body of the message (a plain-text and an HTML version).
    text = "Gitcheck report for %s created on %s\n\n This file can be seen in html only." % (html.path, html.timestamp)
    htmlcontent = "<html>\n<head>\n<h1>Gitcheck Report</h1>\n<h2>%s</h2>\n</head>\n<body>\n<p>%s</p>\n</body>\n</html>" % (html.path,content)
    #Write html file to disk    
    f = open(filepath+'//result.html', 'w')
    f.write(htmlcontent) 
    print ("File saved under %s\\result.html" %filepath) 
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(htmlcontent, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    # Send the message via local SMTP server.
    s = smtplib.SMTP(config['smtp'],config['smtp_port'])
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(config['from'], config['to'], msg.as_string())
    s.quit()

def initEmailConfig():
    config = ConfigObj()
    userPath = expanduser('~')
    saveFilePath = r'%s\Documents\.gitcheck' %(userPath)
    if not os.path.exists(saveFilePath):
        os.makedirs(saveFilePath)
    config.filename = saveFilePath+'\mail.properties'
    #
    config['smtp'] = 'yourServer'
    config['smtp_port'] = 25
    config['from'] = 'from@server.com'
    config['to'] = 'to@server.com'
    
    config.write()
    print ('Please, modify config file located here : %s') % config.filename

       
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
    print("  -e, --email                          Send an email with result as html, using mail.properties parameters")
    print("  --initEmail                          Initialize mail.properties file (has to be modified by user)")

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "vhrbw:i:d:m:q:e",
            ["verbose", "help", "remote", "bell", "watch=", "ignore-branch=",
             "dir=", "maxdepth=", "quiet","email", "initEmail"])
    except getopt.GetoptError, e:
        if e.opt == 'w' and 'requires argument' in e.msg:
            print "Please indicate nb seconds for refresh ex: gitcheck -w10"
        else:
            print e.msg
        sys.exit(2)

    verbose = False
    checkremote = False
    email = False
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
        elif opt in ("-e", "--email"):
            email = True
        elif opt in ("--initEmail"):
            initEmailConfig()
            sys.exit(0)
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
            quiet,
            email
        )
        
        if gitcheck:
            if email:        
                print ("Sending email")
                sendReport(html.msg)

        if watchInterval:
            time.sleep(watchInterval)
        else:
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
