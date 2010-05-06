import os
import re
import subprocess

from rl import completion
from rl import print_exc

from gpgkeys.config import GNUPGEXE
from gpgkeys.config import GNUPGHOME

from gpgkeys.utils import PY3
from gpgkeys.utils import encode
from gpgkeys.utils import b

from completion import quote_string
from completion import dequote_string
from completion import Completion

keyid_re = re.compile(r'^[0-9A-F]+$', re.I)
userid_re = re.compile(r'^(.+?)\s*(?:\((.*)\))*\s*(?:<(.*)>)*$')
escaped_char_re = re.compile(b(r'([\\]x[0-9a-f]{2})'))


def char(int):
    """Create a one-character (byte) string from the ordinal ``int``."""
    if PY3:
        return bytes((int,))
    else:
        return chr(int)


def unescape(text):
    """Convert ``gpg --with-colons`` output to a (byte) string."""
    seen = {}
    for m in escaped_char_re.finditer(text):
        for g in m.groups():
            if g not in seen:
                text = text.replace(g, char(int(g[2:], 16)))
                seen[g] = True
    return text


def decode(text):
    """Decode a GnuPG string."""
    try:
        text = text.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = text.decode('latin-1')
        except UnicodeDecodeError:
            if PY3:
                text = text.decode('utf-8', 'surrogateescape')
            else:
                text = text.decode('utf-8', 'replace')
    return text


def recode(text):
    """Reformat string for display."""
    if PY3:
        return text
    else:
        return encode(decode(text))


class KeyCompletion(Completion):
    """Perform keyid and userid completion

    Watches the keyrings for changes and automatically refreshes
    its completion cache.
    """

    def __init__(self):
        super(KeyCompletion, self).__init__()
        self.pubring = os.path.join(GNUPGHOME, 'pubring.gpg')
        self.secring = os.path.join(GNUPGHOME, 'secring.gpg')
        self.mtimes = (0, 0)
        self.by_keyid = {}
        self.by_userid = {}
        self.by_name = {}

    @print_exc
    def __call__(self, text):
        self.update()
        self.quote_results = False
        matches = []
        if not text or keyid_re.match(text):
            matches = self.complete(self.by_keyid, text.upper())
        if not matches:
            if completion.found_quote:
                text = dequote_string(text, completion.quote_character)
            if completion.quote_character:
                matches = self.complete(self.by_userid, text.lower())
            if not matches:
                matches = self.complete(self.by_name, text.lower())
            if not matches and not completion.quote_character and completion.found_quote:
                matches = self.complete(self.by_userid, text.lower())
        if self.quote_results:
            single_match = len(matches) == 1
            matches = [quote_string(x, single_match, completion.quote_character)
                       for x in matches]
        return matches

    def complete(self, map, text):
        return [self.format(map, x) for x in map if x.startswith(text)]

    def format(self, map, text):
        if map is self.by_keyid:
            if completion.completion_type == '?':
                text = '%s %s' % map[text]
                text = recode(text)
        else:
            text = '%s' % map[text]
            if completion.completion_type == '?':
                text = recode(text)
            else:
                self.quote_results = True
        return text

    def update(self):
        mtimes = (os.stat(self.pubring).st_mtime, os.stat(self.secring).st_mtime)
        if self.mtimes != mtimes:
            self.by_keyid = {}
            self.by_userid = {}
            self.by_name = {}
            for keyid, userid in self.read_keys():
                keyid = keyid[8:]
                self.by_keyid.setdefault(keyid, (keyid, userid))
                self.by_userid.setdefault(userid.lower(), userid)
                for name in self.parse_names(userid):
                    self.by_name.setdefault(name.lower(), name)
            self.mtimes = mtimes

    def read_keys(self):
        process = subprocess.Popen(GNUPGEXE+' --list-keys --with-colons',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return self.parse_keys(stdout)

    def parse_keys(self, stdout):
        for line in stdout.strip().split(b('\n')):
            if line[:3] == b('pub'):
                fields = line.split(b(':'))
                keyid = fields[4]
                userid = unescape(fields[9])
                if PY3:
                    keyid = decode(keyid)
                    userid = decode(userid)
                yield (keyid, userid)

    def parse_names(self, userid):
        m = userid_re.match(userid)
        if m is not None:
            for name in m.group(1).split():
                if len(name) > 1 and not (len(name) == 2 and name[-1] == '.'):
                    yield name

