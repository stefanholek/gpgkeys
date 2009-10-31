import os

from rl import print_exc
from gpgkeys.config import GNUPGHOME


class KeyserverCompletion(object):
    """Perform keyserver completion

    To become available for completion, keyservers must be configured
    in $GNUPGHOME/gpg.conf.
    """

    def __init__(self):
        self.gpgconf = os.path.join(GNUPGHOME, 'gpg.conf')
        self.mtime = 0
        self.servers = []

    @print_exc
    def __call__(self, text):
        self.update_servers()
        return [x for x in self.servers if x.startswith(text)]

    def update_servers(self):
        mtime = os.stat(self.gpgconf).st_mtime
        if self.mtime != mtime:
            self.mtime = mtime
            self.servers = list(self.read_servers())

    def read_servers(self):
        f = open(self.gpgconf, 'rt')
        try:
            config = f.read()
        finally:
            f.close()

        for line in config.strip().split('\n'):
            tokens = line.split()
            if len(tokens) > 1:
                if tokens[0] == 'keyserver':
                    yield tokens[1]
