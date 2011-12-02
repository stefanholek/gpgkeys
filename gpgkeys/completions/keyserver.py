import os

from gpgkeys.config import GNUPGHOME


class KeyserverCompletion(object):
    """Perform keyserver completion

    To become available for completion keyservers must be configured
    in $GNUPGHOME/gpg.conf.
    """

    def __init__(self):
        self.gpgconf = os.path.join(GNUPGHOME, 'gpg.conf')
        self.options = os.path.join(GNUPGHOME, 'options')
        self.mtime = 0
        self.servers = []

    def __call__(self, text):
        self.update()
        return [x for x in self.servers if x.startswith(text)]

    def update(self):
        mtime = os.stat(self.gpgconf).st_mtime
        if self.mtime != mtime:
            self.mtime = mtime
            self.servers = list(self.read_servers())

    def read_servers(self):
        if os.path.isfile(self.gpgconf):
            f = open(self.gpgconf, 'rt')
        elif os.path.isfile(self.options):
            f = open(self.options, 'rt')
        else:
            return []
        try:
            config = f.read()
        finally:
            f.close()
        return self.parse_servers(config)

    def parse_servers(self, config):
        for line in config.strip().split('\n'):
            tokens = line.split()
            if len(tokens) > 1:
                if tokens[0] == 'keyserver':
                    yield tokens[1]
