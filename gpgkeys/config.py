import os

UMASK = 0077

GNUPGEXE = 'gpg2'

GNUPGHOME = os.environ.get('GNUPGHOME', '~/.gnupg')
GNUPGHOME = os.path.abspath(os.path.expanduser(GNUPGHOME))
