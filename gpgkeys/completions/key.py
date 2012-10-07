import os
import sys
import re
import subprocess

from rl import completion

from gpgkeys.config import GNUPGEXE
from gpgkeys.config import GNUPGHOME

from gpgkeys.utils import getpreferredencoding
from gpgkeys.utils import decode
from gpgkeys.utils import encode
from gpgkeys.utils import char
from gpgkeys.utils import b

from kmd.completions.quoting import dequote_string
from kmd.completions.quoting import quote_string

keyid_re = re.compile(r'^[0-9A-F]+$', re.I)
userid_re = re.compile(r'^(.+?)\s*(?:\((.*)\))*\s*(?:<(.*)>)*$')
unescape_re = re.compile(b(r'([\\]x[0-9a-f]{2})'))


def unescape(text):
    """Convert ``gpg --with-colons`` output to a byte string.

    The string is quoted like a C string to avoid control characters.
    The colon is encoded as '\x3a'.
    """
    seen = {}
    for m in unescape_re.finditer(text):
        for g in m.groups():
            if g not in seen:
                text = text.replace(g, char(int(g[2:], 16)))
                seen[g] = True
    return text


def gpgdecode(text):
    """Decode a GnuPG string.

    Returns decoded string and source encoding.
    """
    try:
        encoding = 'utf-8'
        text = decode(text, encoding, errors='strict')
    except UnicodeDecodeError:
        try:
            encoding = 'latin-1'
            text = decode(text, encoding, errors='strict')
        except UnicodeDecodeError:
            encoding = getpreferredencoding()
            text = decode(text, encoding)
    return text, encoding


class KeyCompletion(object):
    """Perform key id and user name completion

    Watches the keyrings for changes and automatically refreshes
    its completion cache.
    """

    def __init__(self):
        self.pubring = os.path.join(GNUPGHOME, 'pubring.gpg')
        self.secring = os.path.join(GNUPGHOME, 'secring.gpg')
        self.mtimes = (0, 0)
        self.encodings = {}
        self.by_keyid = {}
        self.by_userid = {}
        self.by_name = {}

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
        single_match = len(matches) == 1
        if single_match:
            matches = [self.recode(x) for x in matches]
        if self.quote_results:
            matches = [quote_string(x, single_match, completion.quote_character)
                       for x in matches]
        return matches

    def complete(self, map, text):
        return [self.format(map, x) for x in map if x.startswith(text)]

    def format(self, map, text):
        if map is self.by_keyid:
            if completion.completion_type == '?':
                text = '%s %s' % map[text]
        else:
            text = '%s' % map[text]
            if completion.completion_type != '?':
                self.quote_results = True
        return text

    def update(self):
        mtimes = (os.stat(self.pubring).st_mtime, os.stat(self.secring).st_mtime)
        if self.mtimes != mtimes:
            self.encodings = {}
            self.by_keyid = {}
            self.by_userid = {}
            self.by_name = {}
            for keyid, userid in self.read_keys():
                self.by_keyid.setdefault(keyid, (keyid, userid))
                self.by_userid.setdefault(userid.lower(), userid)
                for name in self.parse_names(userid):
                    self.by_name.setdefault(name.lower(), name)
            self.mtimes = mtimes

    def read_keys(self):
        process = subprocess.Popen(GNUPGEXE+' --list-keys --with-colons',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = process.communicate()
        return self.parse_keys(stdoutdata)

    def parse_keys(self, stdoutdata):
        # Process stdoutdata as byte string since we must run
        # unescape before decoding.
        for line in stdoutdata.strip().split(b('\n')):
            if line[:3] == b('pub'):
                fields = line.split(b(':'))
                keyid = fields[4][8:]
                userid = unescape(fields[9])
                keyid, key_enc = gpgdecode(keyid)
                userid, user_enc = gpgdecode(userid)
                if sys.version_info[0] < 3:
                    keyid = encode(keyid)
                    userid = encode(userid)
                self.encodings.setdefault(userid, user_enc)
                yield (keyid, userid)

    def parse_names(self, userid):
        m = userid_re.match(userid)
        if m is not None:
            for name in m.group(1).split():
                if len(name) > 1 and not (len(name) == 2 and name[-1] == '.'):
                    self.encodings.setdefault(name, self.encodings[userid])
                    yield name

    def recode(self, text):
        encoding = self.encodings.get(text)
        if encoding is None:
            return text
        if sys.version_info[0] >= 3:
            # sys.stdin is set up for surrogates in GPGKeys.input()
            return decode(encode(text, encoding), errors='surrogateescape')
        else:
            return encode(decode(text), encoding)

