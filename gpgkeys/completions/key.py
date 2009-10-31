import os
import subprocess

from rl import print_exc
from gpgkeys.config import GNUPGEXE
from gpgkeys.config import GNUPGHOME


class KeyCompletion(object):
    """Perform key id completion

    Watches the keyrings for changes and automatically refreshes
    its completion cache.
    """

    def __init__(self):
        self.pubring = os.path.join(GNUPGHOME, 'pubring.gpg')
        self.secring = os.path.join(GNUPGHOME, 'secring.gpg')
        self.mtimes = (0, 0)
        self.keyspecs = {}

    @print_exc
    def __call__(self, text, keyids_only=True):
        self.update_keys()
        text = text.upper()
        matches = [x for x in self.keyspecs.iterkeys() if x.startswith(text)]
        if len(matches) == 1:
            if keyids_only:
                return [x[0] for x in self.keyspecs[matches[0]]]
            else:
                return ['%s "%s"' % x for x in self.keyspecs[matches[0]]]
        return matches

    def update_keys(self):
        mtimes = (os.stat(self.pubring).st_mtime, os.stat(self.secring).st_mtime)
        if self.mtimes != mtimes:
            keyspecs = {}
            def append(key, value):
                keyspecs.setdefault(key, [])
                keyspecs[key].append(value)

            for keyid, userid in self.read_keys():
                keyid = keyid[8:]
                info = (keyid, userid)
                append('%s %s' % info, info)
            self.mtimes = mtimes
            self.keyspecs = keyspecs

    def read_keys(self):
        process = subprocess.Popen(GNUPGEXE+' --list-keys --with-colons',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        for line in stdout.strip().split('\n'):
            if line[:3] == 'pub':
                fields = line.split(':')
                keyid = fields[4]
                userid = fields[9]
                yield (keyid, userid)

