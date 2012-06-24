import os
import sys
import getopt

from scanner import find_unquoted
from scanner import rfind_unquoted

from splitter import split
from splitter import closequote
from splitter import splitpipe


def splitargs(args):
    """Split the command line into tokens."""
    return closequote(split(args))


def parseargs(args):
    """Parse the command line."""
    mine, pipe = splitpipe(splitargs(args))
    args = Args()
    args.parse(mine)
    args.pipe = pipe
    return args


def parseword(line, begidx, endidx):
    """Parse the completion word."""
    word = Word()
    word.parse(line, begidx, endidx)
    return word


class Args(object):
    """Parse the command line with getopt.
    """

    long_options = ('openpgp',
                    'local-user=',
                    'fingerprint',
                    'with-colons',
                    'clean',
                    'minimal',
                    'merge-only',
                    'armor',
                    'output=',
                    'keyserver=',
                    'expert',
                    'secret',
                    'secret-and-public')

    def __init__(self):
        self.openpgp = False
        self.local_user = None
        self.fingerprint = 0
        self.with_colons = False
        self.merge_only = False
        self.clean = False
        self.minimal = False
        self.armor = False
        self.output = None
        self.keyserver = None
        self.expert = False
        self.secret = False
        self.secret_and_public = False
        self.args = ()
        self.pipe = ()
        self.error = None

    def parse(self, args):
        try:
            options, args = getopt.gnu_getopt(args, '', self.long_options)
        except getopt.GetoptError, e:
            self.error = e
        else:
            for name, value in options:
                if name == '--openpgp':
                    self.openpgp = True
                elif name == '--local-user':
                    self.local_user = value
                elif name == '--fingerprint':
                    self.fingerprint += 1
                elif name == '--with-colons':
                    self.with_colons = True
                elif name == '--merge-only':
                    self.merge_only = True
                elif name == '--clean':
                    self.clean = True
                elif name == '--minimal':
                    self.minimal = True
                elif name == '--armor':
                    self.armor = True
                elif name == '--output':
                    self.output = value
                elif name == '--keyserver':
                    self.keyserver = value
                elif name == '--expert':
                    self.expert = True
                elif name == '--secret':
                    self.secret = True
                elif name == '--secret-and-public':
                    self.secret_and_public = True
            self.args = tuple(args)

    @property
    def ok(self):
        return self.error is None

    @property
    def options(self):
        options = []
        if self.openpgp:
            options.append('--openpgp')
        if self.local_user:
            options.append('--local-user %s' % self.local_user)
        for x in range(self.fingerprint):
            options.append('--with-fingerprint')
        if self.with_colons:
            options.append('--with-colons')
        if self.armor:
            options.append('--armor')
        if self.output:
            options.append('--output %s' % self.output)
        if self.keyserver:
            options.append('--keyserver %s' % self.keyserver)
            options.append('--keyserver-options no-honor-keyserver-url')
        if self.expert:
            options.append('--expert')
        if self.merge_only:
            options.append('--import-options merge-only')
            options.append('--keyserver-options merge-only')
        if self.clean:
            options.append('--import-options import-clean')
            options.append('--export-options export-clean')
            options.append('--keyserver-options import-clean')
            options.append('--keyserver-options export-clean')
        if self.minimal:
            options.append('--import-options import-minimal')
            options.append('--export-options export-minimal')
        return tuple(options)

    @property
    def tuple(self):
        return self.options + self.args + self.pipe


class Word(object):
    """Parse the completion word.
    """

    def parse(self, line, begidx, endidx):
        self.text = line[begidx:endidx]
        self.line = line
        self.begidx = begidx
        self.endidx = endidx

    @property
    def isoption(self):
        return self.text.startswith('-')

    @property
    def isfilename(self):
        return self.text.startswith('~') or (os.sep in self.text)

    def follows(self, text):
        idx = self.line.rfind(text, 0, self.begidx)
        if idx >= 0:
            delta = self.line[idx+len(text):self.begidx]
            if delta.strip() in ('"', "'", ''):
                return True
        return False

    @property
    def commandpos(self):
        delta = self.line[0:self.begidx]
        if delta.strip() in ('!', '.', 'shell'):
            return True
        return False

    @property
    def pipepos(self):
        idx = rfind_unquoted(self.line, self.begidx, ('|', ';'))
        if idx >= 0:
            delta = self.line[idx+1:self.begidx]
            if delta.strip() in ('"', "'", ''):
                # '>|' is not a pipe but an output redirect
                if idx > 0 and self.line[idx] == '|':
                    if rfind_unquoted(self.line, self.begidx, ('>',)) == idx-1:
                        return False
                return True
        return False

    @property
    def filepos(self):
        return find_unquoted(self.line, self.begidx, ('|', '>', '<')) >= 0

