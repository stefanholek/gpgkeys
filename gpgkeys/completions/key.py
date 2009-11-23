import os
import re
import locale
import subprocess

from rl import completion
from rl import print_exc

from gpgkeys.config import GNUPGEXE
from gpgkeys.config import GNUPGHOME
from gpgkeys.completions.filename import dequote_filename
from gpgkeys.completions.filename import quote_filename

keyid_re = re.compile(r'^[0-9A-F]+$', re.I)
userid_re = re.compile(r'^(.+?)\s*(?:\((.*)\))*\s*(?:<(.*)>)*$')
escaped_char_re = re.compile(r'([\\]x[0-9a-f]{2})')


class KeyCompletion(object):
    """Perform keyid and userid completion

    Watches the keyrings for changes and automatically refreshes
    its completion cache.
    """

    def __init__(self):
        self.charset = locale.getlocale()[1]
        self.pubring = os.path.join(GNUPGHOME, 'pubring.gpg')
        self.secring = os.path.join(GNUPGHOME, 'secring.gpg')
        self.mtimes = (0, 0)
        self.by_keyid = {}
        self.by_userid = {}
        self.by_name = {}

    @print_exc
    def __call__(self, text):
        self.update_keys()
        self.quote_results = False
        matches = []

        if not text or keyid_re.match(text):
            matches = self.complete(self.by_keyid, text.upper())

        if not matches:
            if completion.found_quote:
                text = dequote_filename(text, completion.quote_character)
            if completion.quote_character:
                matches = self.complete(self.by_userid, text.lower())
            if not matches:
                matches = self.complete(self.by_name, text.lower())

        if self.quote_results:
            single_match = len(matches) == 1
            matches = [quote_filename(x, single_match, completion.quote_character)
                       for x in matches]
        return matches

    def complete(self, map, text):
        return [self.format(map, x) for x in map if x.startswith(text)]

    def format(self, map, text):
        if map is self.by_keyid:
            if completion.completion_type == '?':
                text = '%s %s' % map[text]
                text = self.recode(text)
        else:
            text = '%s' % map[text]
            if completion.completion_type == '?':
                text = self.recode(text)
            else:
                self.quote_results = True
        return text

    def update_keys(self):
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
        for line in stdout.strip().split('\n'):
            if line[:3] == 'pub':
                fields = line.split(':')
                keyid = fields[4]
                userid = self.unescape(fields[9])
                yield (keyid, userid)

    def parse_names(self, userid):
        m = userid_re.match(userid)
        if m is not None:
            for name in m.group(1).split():
                if len(name) > 1 and not (len(name) == 2 and name[-1] == '.'):
                    yield name

    def unescape(self, text):
        # --with-colons prints some characters in hex
        seen = {}
        for m in escaped_char_re.finditer(text):
            for g in m.groups():
                if g not in seen:
                    text = text.replace(g, chr(int(g[2:], 16)))
                    seen[g] = True
        return text

    def decode(self, text):
        # Userids may contain latin-1
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = text.decode('latin-1')
            except UnicodeDecodeError:
                text = text.decode('utf-8', 'replace')
        return text

    def encode(self, text):
        return text.encode(self.charset)

    def recode(self, text):
        return self.encode(self.decode(text))

