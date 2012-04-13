=========================================================
:mod:`gpgkeys` -- A GnuPG front-end
=========================================================

.. toctree::
   :maxdepth: 2

Commands
==================

:index:`EOF`
------------
End the session.

::

  Usage: Ctrl+D

:index:`checksig`
-----------------
List keys with signatures and also verify the signatures.

::

  Usage: checksig [<keyspec>]
  Options: --fingerprint --with-colons

:index:`clear`
--------------
Clear the terminal screen.

::

  Usage: clear

:index:`del`
------------
Delete a key from the keyring.

::

  Usage: del <keyspec>
  Options: --secret --secret-and-public

:index:`dump`
-------------
Print the packet sequence of keys.

::

  Usage: dump [<keyspec>]
  Options: --clean --minimal --secret

:index:`edit`
-------------
Enter the key edit menu.

::

  Usage: edit <keyspec>
  Options: --expert --local-user --openpgp
  Aliases: e

:index:`export`
---------------
Export keys to stdout or to a file.

::

  Usage: export [<keyspec>]
  Options: --armor --clean --minimal --output --secret

:index:`fdump`
--------------
Print the packet sequence of keys in a file.

::

  Usage: fdump <filename>

:index:`fetch`
--------------
Fetch keys from a URL.

::

  Usage: fetch <url>
  Options: --clean --merge-only

:index:`genkey`
---------------
Generate a new key pair and certificate.

::

  Usage: genkey
  Options: --expert --openpgp

:index:`genrevoke`
------------------
Generate a revocation certificate for a key pair.

::

  Usage: genrevoke <keyspec>
  Options: --armor --openpgp --output

:index:`help`
-------------
Interactive help.

::

  Usage: help [<topic>]
  Aliases: ?

:index:`import`
---------------

Import keys from a file.

::

  Usage: import <filename>
  Options: --clean --merge-only --minimal

:index:`list`
-------------

List keys.

::

  Usage: list [<keyspec>]
  Options: --fingerprint --secret --with-colons
  Aliases: ls

:index:`listsig`
----------------
List keys with signatures.

::

  Usage: listsig [<keyspec>]
  Options: --fingerprint --with-colons
  Aliases: ll

:index:`lsign`
--------------
Sign a key with a local signature.

::

  Usage: lsign <keyspec>
  Options: --local-user --openpgp

:index:`quit`
-------------
End the session.

::

  Usage: quit

:index:`recv`
-------------
Fetch keys from a keyserver.

::

  Usage: recv <keyids>
  Options: --clean --keyserver --merge-only

:index:`refresh`
----------------
Refresh keys from a keyserver.

::

  Usage: refresh [<keyspec>]
  Options: --clean --keyserver

:index:`search`
---------------
Search for keys on a keyserver.

::

  Usage: search <keyspec>
  Options: --clean --keyserver --merge-only

:index:`send`
-------------
Send keys to a keyserver.

::

  Usage: send <keyspec>
  Options: --clean --keyserver

:index:`shell`
--------------
Execute a shell command or start an interactive shell.

::

  Usage: ! [<command>]
  Aliases: .

:index:`sign`
-------------
Sign a key with an exportable signature.

::

  Usage: sign <keyspec>
  Options: --local-user --openpgp

:index:`version`
----------------
Print the GnuPG version.

::

  Usage: version

Options
===============

:index:`armor`
--------------
Produce ASCII-armored output.

::

  Example: export --armor 355A2D28

:index:`clean`
--------------
Remove expired signatures and signatures by keys not on the keyring.

::

  Example: import --clean some-keys.asc

:index:`expert`
---------------
Enable expert mode, thereby unlocking more algorithm choices.

::

  Example: edit --expert 355A2D28

:index:`fingerprint`
--------------------
Include the public key fingerprint in listings. May be specified twice
to include fingerprints of subkeys.

::

  Example: ls --fingerprint 355A2D28

:index:`keyserver`
------------------
Specify the keyserver to use.

::

  Example: send --keyserver hkp://pgp.surfnet.nl 355A2D28

:index:`local-user`
-------------------
Select the identity to use for signing.

::

  Example: sign --local-user F848941B 355A2D28

:index:`merge-only`
-------------------
Never add new keys to the keyring, only update existing ones.

::

  Example: fetch --merge-only http://somewhere.net/some-keys.asc

:index:`minimal`
----------------
Remove all signatures except the most recent self-signatures.

::

  Example: export --minimal 355A2D28

:index:`openpgp`
----------------
Constrain algorithms to OpenPGP defined ones.

::

  Example: genkey --openpgp

:index:`output`
---------------
Specify the output file.

::

  Example: export --output stefan.asc 355A2D28

:index:`secret`
---------------
Operate on the secret key part.

::

  Example: dump --secret 355A2D28

:index:`secret-and-public`
--------------------------
Operate on both secret and public key parts.

::

  Example: del --secret-and-public 355A2D28

:index:`with-colons`
--------------------
Print output fields in colon-separated format.

::

  Example: listsig --with-colons 355A2D28


Indices and Tables
==================

* :ref:`genindex`
* :ref:`search`

