Changelog
=========

2.2 - 2022-11-17
----------------

- Upgrade to rl 3.1 and kmd 2.4.
  [stefan]

- Replace deprecated ``python setup.py test`` in tox.ini.
  [stefan]

- Remove deprecated ``test_suite`` from setup.py.
  [stefan]

- Add a pyproject.toml file.
  [stefan]

- Include tests in sdist but not in wheel.
  [stefan]


2.1 - 2019-03-20
----------------

- Fix import error.
  [stefan]


2.0 - 2019-03-20
----------------

- Try the ``gpg2`` binary first, if not found fall back to ``gpg``.
  [stefan]

- Always add ``--fixed-list-mode`` to ``--with-colons``.
  [stefan]

- Add ``--ask-cert-level`` option.
  [stefan]

- Stop using 2to3.
  [stefan]

- Fix documentation bug: The send command only accepts key IDs.
  [stefan]

- Fix newline glitch in sign and lsign commands.
  [stefan]


1.23 - 2012-10-07
-----------------

- Improve code for the benefit of 2to3.
  [stefan]

- Rewrite Unicode support.
  [stefan]

- Upgrade to rl 2.4 for Python 3.3 support.
  [stefan]


1.22 - 2012-06-24
-----------------

- The ``--keyserver`` option now overrides any preferred keyserver
  configured for a key.
  [stefan]


1.21 - 2012-05-10
-----------------

- Fix verbose output.
  [stefan]

- Switch to a happier looking Sphinx theme.
  [stefan]

- String and filename quoting was not respected when gpgkeys was
  invoked with arguments. Fixed by requiring kmd >= 2.2.
  [stefan]


1.20 - 2012-04-27
-----------------

- Save the tty state before executing subprocesses, restore afterwards.
  [stefan]

- Support Python 2.5.
  [stefan]

- Require term >= 2.0.
  [stefan]


1.19 - 2012-04-14
-----------------

- Include command aliases in help screens.
  [stefan]

- Return useful exit codes when gpgkeys is invoked with arguments.
  [stefan]

- Fix "double prompt" issue when the edit menu was exited with ^D.
  [stefan]

- The import and fdump commands now support input redirection via '<'.
  [stefan]


1.18 - 2011-11-05
-----------------

- In Python 3, make sure the input function accepts surrogates.
  Also see Python `issue 13342`_.
  [stefan]

- Keyserver completion broke when it failed to find a gpg.conf file.
  [stefan]

- The import command ignored option flags when reading from stdin.
  [stefan]

- Add pretty Sphinx-based docs.
  [stefan]

- Require kmd >= 2.1.
  [stefan]

.. _`issue 13342`: http://bugs.python.org/issue13342


1.17 - 2011-10-06
-----------------

- Use the new aliases dictionary to set up command aliases.
  [stefan]

- Make sure error messages go to stderr.
  [stefan]

- Ignore signals when a pager application is in the foreground.
  [stefan]

- Require kmd >= 2.0.
  [stefan]


1.16.1 - 2011-07-25
-------------------

- Fix history file handling silently broken in 1.16.
  [stefan]


1.16 - 2011-07-14
-----------------

- Use kmd.Kmd instead of cmd.Cmd as base class.
  [stefan]

- Depend on rl through the kmd dependency only.
  [stefan]


1.15 - 2011-05-05
-----------------

- Require rl >= 1.14.
  [stefan]


1.14 - 2011-03-24
-----------------

- Add '!' and '.' to shortcut commands so they show up in help.
  [stefan]

- Drop Python 2.5 support in favor of faster byte string operations
  in later Python versions.
  [stefan]


1.13 - 2011-03-11
-----------------

- Require rl >= 1.13.
  [stefan]


1.12 - 2010-05-21
-----------------

- Print help when required command arguments are missing.
  [stefan]

- Require rl >= 1.11.
  [stefan]


1.11 - 2010-05-07
-----------------

- Change an import statement so 2to3 is able to resolve it.
  [stefan]


1.10 - 2010-05-05
-----------------

- Refactor completions: Extract generic parts into base class.
  [stefan]

- Require rl >= 1.10.
  [stefan]


1.9 - 2010-03-07
----------------

- Rename the del command's --all option to --secret-and-public.
  [stefan]

- Require rl >= 1.6.
  [stefan]


1.8.2 - 2010-03-01
------------------

- Fix failing tests under Python 3 on Linux.
  [stefan]


1.8.1 - 2010-02-25
------------------

- Restore Python 2.5 compatibility. D'oh.
  [stefan]


1.8 - 2010-02-25
----------------

- Support Python 3 via distribute.
  [stefan]

- The --fingerprint option may be given more than once.
  [stefan]


1.7.1 - 2010-02-13
------------------

- Depend on rl >= 1.4.1 explicitly so setuptools does not forget to upgrade
  it as well.
  [stefan]


1.7 - 2010-02-13
----------------

- Change license to GPL.
  [stefan]


1.6 - 2010-01-31
----------------

- Add --clean and --minimal import/export options to respective commands.
  [stefan]

- Fix --merge-only import option of keyserver commands.
  [stefan]

- Remove the --yes option again since it has no apparent effect.
  [stefan]


1.5 - 2010-01-26
----------------

- Remove obsolete --secret option from the import command.
  [stefan]

- Userid completion is now triggered by any kind of quoting.
  [stefan]

- Allow to specifiy command line options after the argument.
  [stefan]


1.4 - 2010-01-20
----------------

- Extend the quoting and dequoting API to make it more (re)usable.
  [stefan]

- Dequoting didn't work right when the default quoting character
  was single quote.
  [stefan]

- Tildes in quoted filenames could cause quotes to be closed even
  if the tilde-expanded name matched a directory.
  [stefan]


1.3 - 2010-01-03
----------------

- Cut down on infrastructure slack in filename completion. The
  individual strategies are very small.
  [stefan]

- Remove logging as it clutters up the code.
  [stefan]

- Add an example session to the README.
  [stefan]


1.2 - 2009-11-24
----------------

- Extend keyid completion to also complete userids and names.
  [stefan]

- Extract filename completion functionality into functions,
  as it is useful in other places as well.
  [stefan]


1.1 - 2009-11-16
----------------

- Allow to specify the filename quoting style on the command line
  to ease experimentation.
  [stefan]

- Filename completion: By dequoting early on we can skip a problematic
  hook and regain control over tilde expansion. Also see rl `issue/3`_.
  [stefan]

.. _`issue/3`: http://github.com/stefanholek/rl/issues#issue/3


1.0 - 2009-11-08
----------------

- Initial release.
