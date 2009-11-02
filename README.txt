=======
gpgkeys
=======
----------------------------
Command line shell for GnuPG
----------------------------

Introduction
============

The **gpgkeys** program is a Python application that allows to conveniently
manage GnuPG keys and keyrings.

While probably not very interesting in itself, it serves as example
application and testbed for the development of the rl_ library.

In particular, gpgkeys contains a sophisticated implementation of
**filename completion**, which may one day find its way into a standalone
package or rl_ add-on.

.. _rl: http://pypi.python.org/pypi/rl

Installation
============

gpgkeys depends on the rl_ library. Since rl_ contains a C extension, it
is a good idea to install it independently first.

Once rl_ is installed, type::

    /path/to/easy_install gpgkeys

and bask in the glow.

