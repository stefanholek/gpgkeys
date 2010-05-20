# gpgkeys
#

import locale
locale.setlocale(locale.LC_ALL, '')

import pkg_resources
__version__ = pkg_resources.get_distribution('gpgkeys').version

import os
import sys
import cmd
import atexit
import getopt
import subprocess

from rl import completer
from rl import completion
from rl import history
from rl import readline
from rl import print_exc

from scanner import scan_unquoted
from scanner import rscan_unquoted

from splitter import split
from splitter import closequote
from splitter import splitpipe

from utils import PY3
from utils import decode

from completions.filename import FilenameCompletion
from completions.command import CommandCompletion
from completions.key import KeyCompletion
from completions.keyserver import KeyserverCompletion

from config import GNUPGEXE
from config import UMASK

GLOBAL  = []
KEY     = ['--openpgp']
SIGN    = ['--local-user']
LIST    = ['--fingerprint', '--with-colons']
INPUT   = ['--merge-only']
OUTPUT  = ['--armor', '--output']
CLEAN   = ['--clean']
MINIMAL = ['--minimal']
SERVER  = ['--keyserver']
EXPERT  = ['--expert']
SECRET  = ['--secret']
DELETE  = ['--secret-and-public']


class GPGKeys(cmd.Cmd):
    """Cmd interface for GnuPG with advanced completion capabilities.
    """

    intro = 'gpgkeys %s (type help for help)\n' % __version__
    prompt = 'gpgkeys> '

    doc_header = 'Available commands (type help <topic>):'
    undoc_header = 'Shortcut commands (type help <topic>):'

    nohelp = "gpgkeys: no help on '%s'"

    def __init__(self, completekey='tab', stdin=None, stdout=None,
                 quote_char='\\', verbose=False):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self.quote_char = quote_char
        self.verbose = verbose
        os.umask(UMASK)

    def preloop(self):
        cmd.Cmd.preloop(self)
        self.init_completer(self.quote_char)
        self.init_history()

    # Overrides

    def parseline(self, line):
        # Make '.' work as shell escape character.
        # Make '#' work as comment character.
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!' or line[0] == '.':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        elif line[0] == '#':
            line = ''
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars:
            i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def __getattr__(self, name):
        # Expand unique command prefixes. Thanks to TL.
        if name.startswith(('do_', 'complete_', 'help_')):
            matches = set(x for x in self.get_names() if x.startswith(name))
            if len(matches) == 1:
                return getattr(self, matches.pop())
        raise AttributeError(name)

    # GnuPG runner

    def system(self, *args):
        command = ' '.join(args)
        if self.verbose:
            self.stdout.write('>>> %s\n' % command)
        try:
            process = subprocess.Popen(command, shell=True)
            process.communicate()
            return process.returncode
        except KeyboardInterrupt:
            return 1

    def gnupg(self, *args):
        return self.system(GNUPGEXE, *args)

    # Commands

    def splitargs(self, args):
        # Split the command line into tokens
        return closequote(split(args))

    def parseargs(self, args):
        # Parse the command line
        mine, pipe = splitpipe(self.splitargs(args))
        args = Args()
        args.parse(mine)
        args.pipe = pipe
        return args

    def emptyline(self):
        """Empty line"""
        pass

    def default(self, args):
        """Unknown command"""
        args = self.splitargs(args)
        self.stdout.write('gpgkeys: unknown command: %s\n' % args[0])

    def do_EOF(self, args):
        """End the session (Usage: ^D)"""
        self.stdout.write('\n')
        return self.do_quit(args)

    def do_quit(self, args):
        """End the session (Usage: quit)"""
        return True # Break the cmd loop

    def do_clear(self, args):
        """Clear the terminal screen (Usage: clear)"""
        self.system('clear')

    def do_genkey(self, args):
        """Generate a new key pair and certificate (Usage: genkey)"""
        args = self.parseargs(args)
        if args.ok:
            self.gnupg('--gen-key', *args.tuple)

    def do_genrevoke(self, args):
        """Generate a revocation certificate for a key (Usage: genrevoke <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--gen-revoke', *args.tuple)
            else:
                self.do_help('genrevoke')

    def do_import(self, args):
        """Import keys from a file (Usage: import <filename>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--import', *args.tuple)
            else:
                self.do_help('import')

    def do_export(self, args):
        """Export keys to stdout or to a file (Usage: export [<keyspec>])"""
        args = self.parseargs(args)
        if args.ok:
            command = '--export'
            if args.secret:
                command = '--export-secret-keys'
            self.gnupg(command, *args.tuple)

    def do_list(self, args):
        """List keys (Usage: list [<keyspec>])"""
        args = self.parseargs(args)
        if args.ok:
            command = '--list-keys'
            if args.secret:
                command = '--list-secret-keys'
            self.gnupg(command, *args.tuple)

    def do_ls(self, args):
        self.do_list(args)

    def do_listsig(self, args):
        """List keys including signatures (Usage: listsig [<keyspec>])"""
        args = self.parseargs(args)
        if args.ok:
            self.gnupg('--list-sigs', *args.tuple)

    def do_ll(self, args):
        self.do_listsig(args)

    def do_checksig(self, args):
        """Like listsig, but also verify the signatures (Usage: checksig [<keyspec>])"""
        args = self.parseargs(args)
        if args.ok:
            self.gnupg('--check-sigs', *args.tuple)

    def do_edit(self, args):
        """Enter the key edit menu (Usage: edit <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--edit-key', *args.tuple)
            else:
                self.do_help('edit')

    def do_e(self, args):
        self.do_edit(args)

    def do_lsign(self, args):
        """Sign a key with a local signature (Usage: lsign <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--lsign-key', *args.tuple)
            else:
                self.do_help('lsign')

    def do_sign(self, args):
        """Sign a key with an exportable signature (Usage: sign <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--sign-key', *args.tuple)
            else:
                self.do_help('sign')

    def do_del(self, args):
        """Delete a key from the keyring (Usage: del <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                command = '--delete-key'
                if args.secret:
                    command = '--delete-secret-key'
                if args.secret_and_public:
                    command = '--delete-secret-and-public-key'
                self.gnupg(command, *args.tuple)
            else:
                self.do_help('del')

    def do_search(self, args):
        """Search for keys on a keyserver (Usage: search <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--search-keys', *args.tuple)
            else:
                self.do_help('search')

    def do_recv(self, args):
        """Fetch keys from a keyserver (Usage: recv <keyids>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--recv-keys', *args.tuple)
            else:
                self.do_help('recv')

    def do_send(self, args):
        """Send keys to a keyserver (Usage: send <keyspec>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--send-keys', *args.tuple)
            else:
                self.do_help('send')

    def do_refresh(self, args):
        """Refresh keys from a keyserver (Usage: refresh [<keyspec>])"""
        args = self.parseargs(args)
        if args.ok:
            self.gnupg('--refresh-keys', *args.tuple)

    def do_fetch(self, args):
        """Fetch keys from a URL (Usage: fetch <url>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--fetch-keys', *args.tuple)
            else:
                self.do_help('fetch')

    def do_dump(self, args):
        """List the packet sequence of a key (Usage: dump [<keyspec>])"""
        args = self.parseargs(args)
        if args.ok:
            command = '--export'
            if args.secret:
                command = '--export-secret-keys'
            tuple = args.options + args.args + ('|', GNUPGEXE, '--list-packets') + args.pipe
            self.gnupg(command, *tuple)

    def do_fdump(self, args):
        """List the packet sequence of a key stored in a file (Usage: fdump <filename>)"""
        args = self.parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--list-packets', *args.tuple)
            else:
                self.do_help('fdump')

    def do_shell(self, args):
        """Execute a command or start an interactive shell (Usage: .<command> or .)"""
        args = self.splitargs(args)
        if args:
            cmd = args[0]
            if cmd == 'ls':
                self.shell_ls(*args[1:])
            elif cmd == 'll':
                self.shell_ll(*args[1:])
            elif cmd == 'cd' or cmd == 'chdir':
                self.shell_chdir(*args[1:])
            elif cmd == 'umask':
                self.shell_umask(*args[1:])
            else:
                self.shell_default(*args)
        else:
            self.system(os.environ.get('SHELL'))

    def do_version(self, args):
        """Show the GnuPG version (Usage: version)"""
        self.gnupg('--version')

    # Shell commands

    def getdirectory(self, dir):
        process = subprocess.Popen('cd %s; pwd' % dir,
            shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if PY3:
                stdout = decode(stdout)
            for line in stdout.strip().split('\n'):
                return line

    def shell_ls(self, *args):
        self.system('ls', '-F', *args)

    def shell_ll(self, *args):
        self.system('ls', '-lF', *args)

    def shell_chdir(self, *args):
        if args:
            dir = self.getdirectory(args[0])
        else:
            dir = os.path.expanduser('~')
        if dir:
            try:
                os.chdir(dir)
            except OSError, e:
                self.stdout.write('%s\n' % (e,))

    def shell_umask(self, *args):
        if args:
            if self.system('umask', *args) == 0:
                try:
                    mask = int(args[0], 8)
                except ValueError, e:
                    self.stdout.write('%s\n' % (e,))
                else:
                    if mask < 512:
                        try:
                            os.umask(mask)
                        except OSError, e:
                            self.stdout.write('%s\n' % (e,))
        else:
            self.system('umask')

    def shell_default(self, *args):
        self.system(*args)

    # Completions

    def init_completer(self, quote_char='\\'):
        self.completefilename = FilenameCompletion(quote_char)
        self.completecommand = CommandCompletion()
        self.completekeyspec = KeyCompletion()
        self.completekeyserver = KeyserverCompletion()
        completer.word_break_hook = self.word_break_hook
        completer.display_matches_hook = self.display_matches_hook

    def parseword(self, line, begidx, endidx):
        # Parse the completion word
        word = Word()
        word.parse(line, begidx, endidx)
        return word

    def completebase(self, word, default):
        # Perform completion after pipes and input/output redirects
        if word.pipepos:
            if not word.isfilename:
                return self.completecommand(word.text)
            return self.completefilename(word.text)
        if word.postredir:
            return self.completefilename(word.text)
        return default(word.text)

    def completeoption(self, text, options):
        return [x for x in options if x.startswith(text)]

    def complete_genkey(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + EXPERT)
        return self.completebase(word, self.completedefault)

    def complete_genrevoke(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + OUTPUT)
        if word.follows('--output'):
            return self.completefilename(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_import(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + INPUT + CLEAN + MINIMAL)
        return self.completebase(word, self.completefilename)

    def complete_export(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + OUTPUT + SECRET + CLEAN + MINIMAL)
        if word.follows('--output'):
            return self.completefilename(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_list(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST + SECRET)
        return self.completebase(word, self.completekeyspec)

    def complete_ls(self, text, line, begidx, endidx):
        return self.complete_list(text, line, begidx, endidx)

    def complete_listsig(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST)
        return self.completebase(word, self.completekeyspec)

    def complete_ll(self, text, line, begidx, endidx):
        return self.complete_listsig(text, line, begidx, endidx)

    def complete_checksig(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST)
        return self.completebase(word, self.completekeyspec)

    def complete_edit(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN + EXPERT)
        if word.follows('--local-user'):
            return self.completekeyspec(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_e(self, text, line, begidx, endidx):
        return self.complete_edit(text, line, begidx, endidx)

    def complete_lsign(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN)
        if word.follows('--local-user'):
            return self.completekeyspec(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_sign(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN)
        if word.follows('--local-user'):
            return self.completekeyspec(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_del(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + DELETE + SECRET)
        return self.completebase(word, self.completekeyspec)

    def complete_search(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + INPUT + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_recv(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + INPUT + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_send(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_refresh(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_fetch(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + INPUT + CLEAN)
        return self.completebase(word, self.completedefault)

    def complete_dump(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SECRET + CLEAN + MINIMAL)
        return self.completebase(word, self.completekeyspec)

    def complete_fdump(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL)
        return self.completebase(word, self.completefilename)

    def complete_shell(self, text, line, begidx, endidx):
        word = self.parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL)
        if word.commandpos:
            if not word.isfilename:
                return self.completecommand(word.text)
        return self.completebase(word, self.completefilename)

    # Completion hooks

    @print_exc
    def word_break_hook(self, begidx, endidx):
        # When completing '.<command>' make '.' a word break character.
        # Ditto for '!'.
        origline = completion.line_buffer
        line = origline.lstrip()
        if line[0] in ('!', '.') and line[0] not in completer.word_break_characters:
            stripped = len(origline) - len(line)
            if begidx - stripped == 0:
                return line[0] + completer.word_break_characters

    @print_exc
    def display_matches_hook(self, substitution, matches, max_length):
        # Handle our own display because we can
        num_matches = len(matches)
        if num_matches > completer.query_items >= 0:
            self.stdout.write('\nDisplay all %d possibilities? (y or n)' % num_matches)
            self.stdout.flush()
            while True:
                c = readline.read_key()
                if c in 'yY\x20': # SPACEBAR
                    break
                if c in 'nN\x7f': # RUBOUT
                    self.stdout.write('\n')
                    completion.redisplay(force=True)
                    return
        completion.display_match_list(substitution, matches, max_length)
        completion.redisplay(force=True)

    # Help

    shortcuts = {'ls': 'list',
                 'll': 'listsig',
                 'e':  'edit'}

    def do_help(self, arg):
        """Interactive help (Usage: help <topic>)"""
        if arg:
            arg = self.shortcuts.get(arg, arg)
            try:
                helpfunc = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    dofunc = getattr(self, 'do_' + arg)
                except AttributeError:
                    pass
                else:
                    doc = dofunc.__doc__.strip()
                    if doc:
                        lparen = doc.rfind('(')
                        rparen = doc.rfind(')')
                        help = doc[:lparen-1]
                        usage = doc[lparen+1:rparen]

                        options = []
                        compfunc = getattr(self, 'complete_' + arg, None)
                        if compfunc is not None:
                            options = compfunc('-', '-', 0, 1)

                        self.stdout.write("%s\n" % usage)
                        if options:
                            self.stdout.write("Options: %s\n" % ' '.join(sorted(options)))
                        self.stdout.write("\n%s\n\n" % help)
                        return
                self.stdout.write("%s\n" % (self.nohelp % (arg,)))
            else:
                helpfunc()
        else:
            cmd.Cmd.do_help(self, '')

    # History

    def init_history(self):
        history.max_entries = 250
        histfile = os.path.expanduser('~/.gpgkeys_history')
        history.read_file(histfile)
        atexit.register(history.write_file, histfile)


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
        self.ok = True

    def parse(self, args):
        try:
            options, args = getopt.gnu_getopt(args, '', self.long_options)
        except getopt.GetoptError, e:
            print >>sys.stderr, 'gpgkeys:', e
            self.ok = False
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
        self.line = line
        self.text = line[begidx:endidx]
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
        idx = rscan_unquoted(self.line, self.begidx, ('|', ';'))
        if idx >= 0:
            delta = self.line[idx+1:self.begidx]
            if delta.strip() in ('"', "'", ''):
                # '>|' is not a pipe but an output redirect
                if idx > 0 and self.line[idx] == '|':
                    if rscan_unquoted(self.line, self.begidx, ('>',)) == idx-1:
                        return False
                return True
        return False

    @property
    def postredir(self):
        return scan_unquoted(self.line, self.begidx, ('|', '>', '<')) >= 0


def main(args=None):
    quote_char = '\\'
    verbose = False

    if args is None:
        args = sys.argv[1:]

    try:
        options, args = getopt.getopt(args, 'hq:v', ('help', 'quote-char=', 'verbose'))
    except getopt.GetoptError, e:
        print >>sys.stderr, 'gpgkeys:', e
        return 1

    for name, value in options:
        if name in ('-q', '--quote-char'):
            quote_char = value
        elif name in ('-v', '--verbose'):
            verbose = True
        elif name in ('-h', '--help'):
            print "Type 'gpgkeys' to start the shell"
            return 0

    shell = GPGKeys(quote_char=quote_char, verbose=verbose)
    if args:
        shell.onecmd(' '.join(args))
    else:
        try:
            shell.cmdloop()
        except KeyboardInterrupt:
            print
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

