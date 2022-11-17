=======
gpgkeys
=======
---------------------
A GnuPG Shell
---------------------

Overview
============

**gpgkeys** is a Python program that allows to conveniently manage GnuPG_ keys
and keyrings from the command line.
It comes in the form of a shell, with commands resembling GnuPG CLI commands and
their options.
Its main feature is end-to-end tab completion.

gpgkeys also serves as testbed for the development of the kmd_ and rl_ Python
libraries.

.. _GnuPG: http://www.gnupg.org/
.. _kmd: https://github.com/stefanholek/kmd
.. _rl: https://github.com/stefanholek/rl

Motivation
==========

The GnuPG CLI is very powerful – and with great power comes
great incomprehensibility.

gpgkeys makes key management easy by:

1. Providing a sensible subset of GnuPG commands, and
2. Using tab completion to streamline the input process and
   guide the user through key management tasks.

Example Session
===============

Everything in gpgkeys can be tab completed: commands, help topics, option flags,
key ids, user names, file names, shell commands, and keyserver URLs.
::

    $ gpgkeys
    gpgkeys 2.2 (type help for help)

    gpgkeys> help

    Available commands (type help <topic>):
    =======================================
    checksig  dump    fdump   genrevoke  list     quit     search  sign
    clear     edit    fetch   help       listsig  recv     send    version
    del       export  genkey  import     lsign    refresh  shell

    Shortcut commands (type help <topic>):
    ======================================
    !  .  ?  e  ll  ls

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

    gpgkeys> export --armor 355A2D28 > stefan.asc
    gpgkeys> .ls
    alice.asc             stefan.asc

Features
============

The order of options and arguments on the command line is not important::

    gpgkeys> export 355A2D28 --armor > stefan.asc

Command lines prefixed with '.' or '!' are executed by the shell.
You can use ``cd`` to change the current directory,
``umask`` to change the umask, and of course everything else::

    gpgkeys> .cd subdir/
    gpgkeys> .pwd
    /home/stefan/subdir

You can use input/output redirects and pipes::

    gpgkeys> export 355A2D28 | pgpdump | less

To see the commands sent to GnuPG, run gpgkeys with the
``-v`` option::

    $ gpgkeys -v
    gpgkeys 2.2 (type help for help)

    gpgkeys> ls 355A2D28
    gpgkeys: gpg --list-keys 355A2D28
    pub   1024D/355A2D28 2001-11-04
    uid                  Stefan H. Holek <stefan@epy.co.at>
    sub   2048g/A27E0DBC 2004-10-27

For everything you ever wanted to know about GnuPG commands, type::

    gpgkeys> .man gpg

gpgkeys can be invoked with arguments, in which case it does not enter
the command loop::

    $ gpgkeys export --armor 355A2D28 > stefan.asc

Keyservers
==========

For the send, recv, search, and refresh commands to work, at least one
keyserver should be configured in gpg.conf. For example::

    keyserver ldap://keyserver.pgp.com
    keyserver hkps://hkps.pool.sks-keyservers.net

The last keyserver in gpg.conf becomes the default keyserver.
All keyservers become available for completion after the ``--keyserver`` option.

Unicode
=======

OpenPGP allows user IDs to be either Latin-1 or UTF-8 encoded.
To find keys with non-ASCII IDs, GnuPG requires search strings to be
encoded the right way.

gpgkeys' key completion keeps track of the original encodings, and every name
you tab-complete will automatically be encoded the way GnuPG expects.
You may sometimes see '?' characters in place of non-ASCII characters on the
command line, which are a result of the above and no reason for concern.

Development
===========

gpgkeys development is hosted on GitHub_. It also has an `issue tracker`_ there.

.. _GitHub: https://github.com/stefanholek/gpgkeys
.. _`issue tracker`: https://github.com/stefanholek/gpgkeys/issues

Installation
============

Installation requires Python 2.7 or higher.

Note: gpgkeys uses the rl_ library which contains a C extension. It is a good
idea to review its `installation instructions`_ and make sure all dependencies
are in place.

To install the ``gpgkeys`` script, type::

    pip install gpgkeys

.. _rl: https://github.com/stefanholek/rl
.. _`installation instructions`: https://github.com/stefanholek/rl#installation

Then put it on your system PATH by e.g. symlinking it to ``/usr/local/bin``.

Requirements
============

Either the ``gpg2`` command or the ``gpg`` command must be available on the
system PATH.

