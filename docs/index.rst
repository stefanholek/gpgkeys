=========================================================
:mod:`gpgkeys` -- A GnuPG front-end
=========================================================

.. toctree::
   :maxdepth: 2

Commands
==================

EOF
---
End the session.

::

  Usage: Ctrl+D

checksig
--------
List keys with signatures and also verify the signatures.

::

  Usage: checksig [<keyspec>]
  Options: --fingerprint --with-colons

clear
-----
Clear the terminal screen.

::

  Usage: clear

del
---
Delete a key from the keyring.

::

  Usage: del <keyspec>
  Options: --secret --secret-and-public

dump
----
Print the packet sequence of keys.

::

  Usage: dump [<keyspec>]
  Options: --clean --minimal --secret

edit
----
Enter the key edit menu.

::

  Usage: edit <keyspec>
  Options: --expert --local-user --openpgp
  Aliases: e

export
------
Export keys to stdout or to a file.

::

  Usage: export [<keyspec>]
  Options: --armor --clean --minimal --output --secret

fdump
-----
Print the packet sequence of keys in a file.

::

  Usage: fdump <filename>

fetch
-----
Fetch keys from a URL.

::

  Usage: fetch <url>
  Options: --clean --merge-only

genkey
------
Generate a new key pair and certificate.

::

  Usage: genkey
  Options: --expert --openpgp

genrevoke
---------
Generate a revocation certificate for a key pair

::

  Usage: genrevoke <keyspec>
  Options: --armor --openpgp --output

help
----
Interactive help.

::

  Usage: help [<topic>]
  Aliases: ?

import
------

Import keys from a file.

::

  Usage: import <filename>
  Options: --clean --merge-only --minimal

list
----

List keys.

::

  Usage: list [<keyspec>]
  Options: --fingerprint --secret --with-colons
  Aliases: ls

listsig
-------
List keys with signatures.

::

  Usage: listsig [<keyspec>]
  Options: --fingerprint --with-colons
  Aliases: ll

lsign
-----
Sign a key with a local signature.

::

  Usage: lsign <keyspec>
  Options: --local-user --openpgp

quit
----
End the session.

::

  Usage: quit

recv
----
Fetch keys from a keyserver.

::

  Usage: recv <keyids>
  Options: --clean --keyserver --merge-only

refresh
-------
Refresh keys from a keyserver.

::

  Usage: refresh [<keyspec>]
  Options: --clean --keyserver

search
------
Search for keys on a keyserver.

::

  Usage: search <keyspec>
  Options: --clean --keyserver --merge-only

send
----
Send keys to a keyserver.

::

  Usage: send <keyspec>
  Options: --clean --keyserver

shell
-----
Execute a shell command or start an interactive shell.

::

  Usage: ! [<command>]
  Aliases: .

sign
----
Sign a key with an exportable signature.

::

  Usage: sign <keyspec>
  Options: --local-user --openpgp

version
-------
Print the GnuPG version.

::

  Usage: version

Options
===============

armor
-----
Produce ASCII-armored output.

::

  Usage: export --armor 355A2D28

clean
-----
Remove expired signatures and signatures by keys not on the keyring.

::

  Usage: import --clean new-keys.asc

expert
------
Enable expert mode, thereby unlocking more algorithm choices.

::

  Usage: edit --expert 355A2D28

fingerprint
-----------
Include the public key fingerprint in listings. May be specified twice
to include fingerprints of subkeys.

::

  Usage: ls --fingerprint 355A2D28

keyserver
---------
Specify the keyserver to use.

::

  Usage: send --keyserver hkp://pgp.surfnet.nl 355A2D28

local-user
----------
Select the identity to use for signing.

::

  Usage: sign --local-user F848941B 355A2D28

merge-only
----------
Never add new keys to the keyring, only update existing ones.

::

  Usage: fetch --merge-only http://somewhere.net/some-keys.asc

minimal
-------
Remove all signatures except the most recent self-signatures.

::

  Usage: export --minimal 355A2D28

openpgp
-------
Constrain algorithms to OpenPGP defined ones.

::

  Usage: genkey --openpgp

output
------
Specify the output file.

::

  Usage: export --output stefan.asc 355A2D28

secret
------
Operate on the secret key part.

::

  Usage: dump --secret 355A2D28

secret-and-public
-----------------
Operate on both secret and public key parts.

::

  Usage: del --secret-and-public 355A2D28

with-colons
-----------
Print output fields in colon-separated format.

::

  Usage: listsig --with-colons 355A2D28


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

