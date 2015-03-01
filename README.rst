gitcheck
========

When working simultaneously on several git repositories, it is easy to
loose the overview on the advancement of your work.  This is why I
decided to write gitcheck, a tool which reports the status of the
repositories it finds in a file tree.  This report can of course be
displayed on the terminal but also be sent by email.


Installation
------------

::

    pip install git+git://github.com/badele/gitcheck.git


Examples
--------

Simple report
~~~~~~~~~~~~~

In a simple invocation, gitcheck shows for each repository found in
the file tree rooted at the current working directory if they have
changes to be committed or commits to be pushed.

.. code:: bash

    >gitcheck.py

.. figure:: http://bruno.adele.im/static/gitcheck.png
   :alt: Gitcheck simple report

   Gitcheck simple report

Detailed report
~~~~~~~~~~~~~~~

This invocation is substantially identical to the previous one, but
the generated report also enumerates modified files and pending
commits.

.. code:: bash

    >gitcheck.py -v

.. figure:: http://bruno.adele.im/static/gitcheck_verbose.png
   :alt: Gitcheck detailed report

   Gitcheck detailed report

Options
~~~~~~~

.. code:: plaintext

    -v, --verbose                     		Show files & commits
    --debug                     		    Show debug message
    -r, --remote                      		also check with the remote
    -b, --bell                        		bell on action needed
    -w <sec>, --watch <sec>           		after displaying, wait <sec> and run again
    -i <re>, --ignore-branch <re>     		ignore branches matching the regex <re>
    -d <dir>, --dir                   		Search <dir> for repositories
	-m <maxdepth>, --maxdepth=<maxdepth> 	Limit the depth of repositories search")
    -q, --quiet                          	Display info only when repository needs action")
    -e, --email                          	Send an email with result as html, using mail.properties parameters")
    --init-email                          	Initialize mail.properties file (has to be modified by user using JSON format)")
	

French version
~~~~~~~~~~~~~~

A French version of this document is available here:
http://bruno.adele.im/projets/gitcheck/
