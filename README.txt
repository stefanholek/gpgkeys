=======
gpgkeys
=======
----------------------------
Command line shell for GnuPG
----------------------------

Introduction
============

**gpgkeys** is a Python program that allows to conveniently
manage GnuPG keys and keyrings.

It serves as example application and testbed for the development of the
rl_ library. In particular, gpgkeys contains a sophisticated implementation of
`filename completion`_ which may one day find its way into a standalone
package or rl_ add-on.

.. _rl: http://pypi.python.org/pypi/rl
.. _`filename completion`: http://github.com/stefanholek/gpgkeys/tree/master/gpgkeys/completions

Repository Access
-----------------

gpgkeys development is hosted on github_.

.. _github: http://github.com/stefanholek/gpgkeys

Installation
============

gpgkeys uses the rl_ library. Since rl_ contains a C extension, it is
a good idea to review its `installation instructions`_ and make sure
all dependencies are in place.

To install the ``gpgkeys`` script, type::

    easy_install gpgkeys

Then put it on your system PATH by e.g.  symlinking it to ``/usr/local/bin``.

.. _`installation instructions`: http://pypi.python.org/pypi/rl#installation

Example Session
===============

Everything in gpgkeys can be tab-completed: commands, help
topics, userids, option flags, keyids, filenames, shell
commands, and keyserver URLs (not shown).
::

    $ gpgkeys
    gpgkeys 1.10 (type help for help)

    gpgkeys> help

    Available commands (type help <topic>):
    =======================================
    EOF       del   export  genkey     import   lsign  refresh  shell
    checksig  dump  fdump   genrevoke  list     quit   search   sign
    clear     edit  fetch   help       listsig  recv   send     version

    Shortcut commands (type help <topic>):
    ======================================
    e  ll  ls

    gpgkeys> help export
    Usage: export <keyspec>
    Options: --armor --clean --minimal --output --secret

    Export keys to stdout or to a file

    gpgkeys> ls Stefan
    pub   1024R/E1F438AD 1995-10-03
    uid                  Stefan H. Holek (RSA) <stefan@epy.co.at>

    pub   1024D/355A2D28 2001-11-04
    uid                  Stefan H. Holek <stefan@epy.co.at>
    sub   2048g/A27E0DBC 2004-10-27

    gpgkeys> export --armor E1F438AD > stefan.asc
    gpgkeys> .ls
    alice.asc             stefan.asc

Note that gpgkeys understands shell pipes and input/output redirects. This
enables command lines like::

    gpgkeys> export E1F438AD | pgpdump | less

