import os

from distutils.spawn import find_executable

UMASK = 0o077

GNUPGEXE = 'gpg2'
if not find_executable('gpg2') and find_executable('gpg'):
    GNUPGEXE = 'gpg'

GNUPGHOME = os.environ.get('GNUPGHOME', '~/.gnupg')
GNUPGHOME = os.path.abspath(os.path.expanduser(GNUPGHOME))

GNUPGCONF = os.path.join(GNUPGHOME, 'gpg.conf')
