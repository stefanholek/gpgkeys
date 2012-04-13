=======
gpgkeys
=======
---------------------
A front-end for GnuPG
---------------------

Introduction
============

**gpgkeys** is a Python program that allows to conveniently manage GnuPG_ keys
and keyrings from the command line.
It comes in the form of a shell, with commands resembling GnuPG CLI commands and
their options.
Its main feature is end-to-end TAB completion.

gpgkeys also serves as testbed for the development of the kmd_ and rl_ Python
libraries.

.. _GnuPG: http://www.gnupg.org/
.. _kmd: http://pypi.python.org/pypi/kmd
.. _rl: http://pypi.python.org/pypi/rl

Motivation
----------

The GnuPG CLI is very powerful - and with great power comes
great incomprehensibility.

gpgkeys makes key management easy by:

1. Providing a sensible subset of GnuPG commands, and

2. Using TAB completion to streamline the input process and guide the user
   through key management tasks.

Example Session
---------------

Everything in gpgkeys can be TAB completed: commands, help topics, option flags,
key ids, user names, file names, shell commands, and keyserver URLs.
::

    $ gpgkeys
    gpgkeys 1.19 (type help for help)

    gpgkeys> help

    Available commands (type help <topic>):
    =======================================
    EOF       del   export  genkey     import   lsign  refresh  shell
    checksig  dump  fdump   genrevoke  list     quit   search   sign
    clear     edit  fetch   help       listsig  recv   send     version

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

Some Details
------------

gpgkeys understands shell pipes and input/output redirects. This
allows command lines like::

    gpgkeys> export 355A2D28 | pgpdump | less

To see the commands gpgkeys sends to GnuPG, run gpgkeys with the
``-v`` option::

    $ gpgkeys -v
    gpgkeys 1.19 (type help for help)

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
----------

For the recv, refresh, search, and send commands to work nicely, at least one
keyserver should be configured in gpg.conf. For example::

    keyserver ldap://keyserver.pgp.com
    keyserver hkp://pgp.surfnet.nl

The last keyserver in gpg.conf becomes the default keyserver.
All keyservers become available for completion after the ``--keyserver`` option.

Unicode
-------

The OpenPGP standard allows user IDs to be either Latin-1 or UTF-8 encoded.
In order to locate a key via a non-ASCII name, GnuPG requires the
search string to be encoded correctly. In other words, to match a Latin-1 name
the search string must itself be Latin-1.

gpgkeys' key completion keeps track of the original encodings, and every name
you TAB complete is automatically encoded to match GnuPG's expectations.
You may sometimes see ? characters in place of non-ASCII characters on the
command line, which are the result of the above and no reason for concern.

Development
===========

gpgkeys development is hosted on GitHub_. It also has an `issue tracker`_ there.

.. _GitHub: https://github.com/stefanholek/gpgkeys
.. _`issue tracker`: https://github.com/stefanholek/gpgkeys/issues

Installation
============

Installation requires Python 2.6 or higher.

gpgkeys depends on kmd_, which in turn uses the rl_ library. Since rl
contains a C extension, it is a good idea to review its `installation
instructions`_ and make sure all dependencies are in place.

To install the ``gpgkeys`` script, type::

    easy_install gpgkeys

Then put it on your system PATH by e.g.  symlinking it to ``/usr/local/bin``.

.. _`installation instructions`: http://pypi.python.org/pypi/rl#installation

Requirements
============

The ``gpg`` command must be available on the system PATH.

