# gpgkeys
#

import os
import sys
import cmd
import atexit
import subprocess

from rl import completer
from rl import completion
from rl import history
from rl import print_exc

from escape import split

from filename import Logging
from filename import FilenameCompletion

gnupg_exe = 'gpg'

GNUPGHOME = os.environ.get('GNUPGHOME', '~/.gnupg')
GNUPGHOME = os.path.abspath(os.path.expanduser(GNUPGHOME))

UMASK = 0077
LOGGING = False

GLOBAL = []
KEY    = ['--openpgp']
SIGN   = ['--local-user']
CHECK  = [] #['--trusted-key']
LIST   = ['--fingerprint', '--with-colons']
INPUT  = ['--merge-only']
OUTPUT = ['--armor', '--output']
SERVER = ['--keyserver']
EXPERT = ['--expert']


class GPGKeys(cmd.Cmd):
    """Cmd interface for GnuPG with advanced completion capabilities.
    """

    intro = 'gpgkeys 1.0 (type help for help)\n'
    prompt = 'gpgkeys> '

    doc_header = 'Available commands (type help <topic>):'
    undoc_header = 'Shortcut commands (type help <topic>):'

    nohelp = "gpgkeys: no help on '%s'"

    def __init__(self, completekey='tab', stdin=None, stdout=None, verbose=False):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self.verbose = verbose
        os.umask(UMASK)

    def preloop(self):
        cmd.Cmd.preloop(self)
        self.init_completer(LOGGING)
        self.init_history()

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
        return self.system(gnupg_exe, *args)

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

    # Commands

    def emptyline(self):
        pass

    def default(self, args):
        args = split(args)
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
        """Generate a new key pair (Usage: genkey)"""
        args = split(args)
        self.gnupg('--gen-key', *args)

    def do_genrevoke(self, args):
        """Generate a revocation certificate for a key (Usage: genrevoke <keyspec>)"""
        args = split(args)
        self.gnupg('--gen-revoke', *args)

    def do_import(self, args):
        """Import public keys from a file (Usage: import <filename>)"""
        args = fix_merge_only(split(args))
        self.gnupg('--import', *args)

    def do_importsec(self, args):
        """Import secret and public keys from a file (Usage: importsec <filename>)"""
        args = fix_merge_only(split(args))
        self.gnupg('--import --allow-secret-key', *args)

    def do_export(self, args):
        """Export public keys to stdout or to a file (Usage: export <keyspec>)"""
        args = split(args)
        self.gnupg('--export', *args)

    def do_exportsec(self, args):
        """Export secret keys to stdout or to a file (Usage: exportsec <keyspec>)"""
        args = split(args)
        self.gnupg('--export-secret-keys', *args)

    def do_list(self, args):
        """List public keys (Usage: list <keyspec>)"""
        args = split(args)
        self.gnupg('--list-keys', *args)

    def do_ls(self, args):
        self.do_list(args)

    def do_listsec(self, args):
        """List secret keys (Usage: listsec <keyspec>)"""
        args = split(args)
        self.gnupg('--list-secret-keys', *args)

    def do_listsig(self, args):
        """List public keys including signatures (Usage: listsig <keyspec>)"""
        args = split(args)
        self.gnupg('--list-sigs', *args)

    def do_ll(self, args):
        self.do_listsig(args)

    def do_checksig(self, args):
        """Like listsig, but also verify the signatures (Usage: checksig <keyspec>)"""
        args = split(args)
        self.gnupg('--check-sigs', *args)

    def do_edit(self, args):
        """Enter the key edit menu (Usage: edit <keyspec>)"""
        args = split(args)
        self.gnupg('--edit-key', *args)

    def do_e(self, args):
        self.do_edit(args)

    def do_lsign(self, args):
        """Sign a key with a local signature (Usage: lsign <keyspec>)"""
        args = split(args)
        self.gnupg('--lsign-key', *args)

    def do_sign(self, args):
        """Sign a key with an exportable signature (Usage: sign <keyspec>)"""
        args = split(args)
        self.gnupg('--sign-key', *args)

    def do_del(self, args):
        """Delete a public key (Usage: del <keyspec>)"""
        args = split(args)
        self.gnupg('--delete-key', *args)

    def do_delsec(self, args):
        """Delete a secret key (Usage: delsec <keyspec>)"""
        args = split(args)
        self.gnupg('--delete-secret-key', *args)

    def do_delsecpub(self, args):
        """Delete both secret and public keys (Usage: delsecpub <keyspec>)"""
        args = split(args)
        self.gnupg('--delete-secret-and-public-key', *args)

    def do_search(self, args):
        """Search for keys on the keyserver (Usage: search <keyspec>)"""
        args = split(args)
        self.gnupg('--search-keys', *args)

    def do_recv(self, args):
        """Fetch keys from the keyserver (Usage: recv <keyids>)"""
        args = fix_merge_only(split(args))
        self.gnupg('--recv-keys', *args)

    def do_send(self, args):
        """Send keys to the keyserver (Usage: send <keyspec>)"""
        args = split(args)
        self.gnupg('--send-keys', *args)

    def do_refresh(self, args):
        """Refresh keys from the keyserver (Usage: refresh <keyspec>)"""
        args = fix_merge_only(split(args))
        self.gnupg('--refresh-keys', *args)

    def do_fetch(self, args):
        """Fetch keys from a URL (Usage: fetch <url>)"""
        args = fix_merge_only(split(args))
        self.gnupg('--fetch-keys', *args)

    def do_dump(self, args):
        """Dump packet sequence of a public key (Usage: dump <keyspec>)"""
        args, pipe = splitpipe(split(args))
        args = ('--export',) + args + ('|', gnupg_exe, '--list-packets') + pipe
        self.gnupg(*args)

    def do_dumpsec(self, args):
        """Dump packet sequence of a secret key (Usage: dumpsec <keyspec>)"""
        args, pipe = splitpipe(split(args))
        args = ('--export-secret-keys',) + args + ('|', gnupg_exe, '--list-packets') + pipe
        self.gnupg(*args)

    def do_fdump(self, args):
        """Dump packet sequence stored in file (Usage: fdump <filename>)"""
        args = split(args)
        self.gnupg('--list-packets', *args)

    def do_shell(self, args):
        """Execute a command or start an interactive shell (Usage: .<command> or .)"""
        args = split(args)
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

    def shell_ls(self, *args):
        self.system('ls', '-F', *args)

    def shell_ll(self, *args):
        self.system('ls', '-lF', *args)

    def shell_getdir(self, dir):
        process = subprocess.Popen('cd %s; pwd' % dir,
            shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            for line in stdout.strip().split('\n'):
                return line

    def shell_chdir(self, *args):
        if args:
            dir = self.shell_getdir(args[0])
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

    def init_completer(self, do_log=False):
        self.completefilenames = FilenameCompletion(do_log, bash=True)
        self.completecommands = CommandCompletion(do_log)
        self.completekeys = KeyCompletion()
        self.completekeyservers = KeyserverCompletion()
        completer.word_break_hook = self.word_break_hook
        completer.display_matches_hook = self.display_matches_hook

    def isoption(self, text):
        # True if 'text' is an option flag
        return text.startswith('-')

    def isfilename(self, text):
        # True if 'text' is a filename
        return (os.sep in text or text.startswith('~'))

    def follows(self, text, line, begidx):
        # True if the completion follows 'text'
        idx = line.rfind(text, 0, begidx)
        if idx >= 0:
            delta = line[idx+len(text):begidx]
            return delta.strip() in ('"', "'", '')
        return False

    def commandpos(self, line, begidx):
        # True if the completion is a shell command at position 0
        delta = line[0:begidx]
        return delta.strip() in ('!', '.', 'shell')

    def postpipe(self, line, begidx):
        # True if the completion follows a pipe or semicolon
        delta = line[0:begidx]
        return delta.strip()[-1:] in ('|', ';')

    def postredir(self, line, begidx):
        # True if the completion is anywhere after a shell redirect
        return (line.rfind('|', 0, begidx) >= 0 or
                line.rfind('>', 0, begidx) >= 0 or
                line.rfind('<', 0, begidx) >= 0)

    def basecomplete(self, text, line, begidx, default):
        if self.postpipe(line, begidx):
            if not self.isfilename(text):
                return self.completecommands(text)
            return self.completefilenames(text)
        if self.postredir(line, begidx):
            return self.completefilenames(text)
        return default(text)

    def completefilenames_(self, text, line, begidx):
        return self.basecomplete(text, line, begidx, self.completefilenames)

    def completekeys_(self, text, line, begidx):
        return self.basecomplete(text, line, begidx, self.completekeys)

    def completedefault_(self, text, line, begidx):
        return self.basecomplete(text, line, begidx, self.completedefault)

    def completeoptions(self, text, options):
        return [x for x in options if x.startswith(text)]

    # Completion grid

    def complete_genkey(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + EXPERT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completedefault_(text, line, begidx)

    def complete_genrevoke(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + OUTPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefilenames(text)
        return self.completekeys_(text, line, begidx)

    def complete_import(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completefilenames_(text, line, begidx)

    def complete_importsec(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completefilenames_(text, line, begidx)

    def complete_export(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefilenames(text)
        return self.completekeys_(text, line, begidx)

    def complete_exportsec(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefilenames(text)
        return self.completekeys_(text, line, begidx)

    def complete_list(self, text, line, begidx, endidx):
        options = GLOBAL + LIST
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_ls(self, text, line, begidx, endidx):
        return self.complete_list(text, line, begidx, endidx)

    def complete_listsec(self, text, line, begidx, endidx):
        options = GLOBAL + LIST
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_listsig(self, text, line, begidx, endidx):
        options = GLOBAL + LIST
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_ll(self, text, line, begidx, endidx):
        return self.complete_listsig(text, line, begidx, endidx)

    def complete_checksig(self, text, line, begidx, endidx):
        options = GLOBAL + LIST + CHECK
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_edit(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + SIGN + EXPERT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_e(self, text, line, begidx, endidx):
        return self.complete_edit(text, line, begidx, endidx)

    def complete_lsign(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + SIGN
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_sign(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + SIGN
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_del(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_delsec(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_delsecpub(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_search(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyservers(text)
        return self.completekeys_(text, line, begidx)

    def complete_recv(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyservers(text)
        return self.completekeys_(text, line, begidx)

    def complete_send(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyservers(text)
        return self.completekeys_(text, line, begidx)

    def complete_refresh(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyservers(text)
        return self.completekeys_(text, line, begidx)

    def complete_fetch(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completedefault_(text, line, begidx)

    def complete_dump(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_dumpsec(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completekeys_(text, line, begidx)

    def complete_fdump(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completefilenames_(text, line, begidx)

    def complete_shell(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.commandpos(line, begidx):
            if not self.isfilename(text):
                return self.completecommands(text)
        return self.completefilenames_(text, line, begidx)

    # Completion hooks

    @print_exc
    def word_break_hook(self, begidx, endidx):
        # If we are completing '.<command>' make '.' a word break
        # character. Same for '!'.
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
        if num_matches > completer.query_items > 0:
            self.stdout.write('\nDisplay all %d possibilities? (y or n)' % num_matches)
            self.stdout.flush()
            while True:
                c = completion.read_key()
                if c in 'yY\x20': # SPACEBAR
                    break
                if c in 'nN\x7f': # RUBOUT
                    self.stdout.write('\n')
                    completion.redisplay(force=True)
                    return
        completion.display_match_list(substitution, matches, max_length)

    # Help

    shortcuts = {'ls': 'list',
                 'll': 'listsig',
                 'e':  'edit'}

    def expandshortcut(self, arg):
        if self.shortcuts.has_key(arg):
            arg = self.shortcuts.get(arg)
        return arg

    def do_help(self, arg):
        """Interactive help (Usage: help <topic>)"""
        if arg:
            arg = self.expandshortcut(arg)
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + arg).__doc__
                    if doc:
                        doc = str(doc)
                        lparen = doc.rfind('(')
                        rparen = doc.rfind(')')
                        usage = doc[lparen+1:rparen]
                        doc = doc[:lparen-1]

                        self.stdout.write("%s\n" % usage)

                        opts = []
                        func = getattr(self, 'complete_' + arg, None)
                        if func is not None:
                            opts = func('-', '', 0, 0)
                            if opts:
                                opts.sort()
                                self.stdout.write("Options: %s\n" % ' '.join(opts))

                        self.stdout.write("\n")
                        self.stdout.write("%s\n" % doc)
                        self.stdout.write("\n")
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
            else:
                func()
        else:
            cmd.Cmd.do_help(self, '')

    # History

    def init_history(self):
        histfile = os.path.expanduser('~/.gpgkeys_history')
        history.read_file(histfile)
        history.length = 100
        atexit.register(history.write_file, histfile)


def splitpipe(args):
    """Split args tuple at first '|' or '>' or '2>' or '<'.
    """
    pipe = ()
    for i in range(len(args)):
        a = args[i]
        if a and a.startswith(('|', '>', '2>', '<')):
            pipe = args[i:]
            args = args[:i]
            break
    return args, pipe


def fix_merge_only(args):
    # gpg: WARNING: "--merge-only" is a deprecated option
    # gpg: please use "--import-options merge-only" instead
    for i in range(len(args)):
        a = args[i]
        if a == '--merge-only':
            args = args[:i] + ('--import-options', 'merge-only') + args[i+1:]
            break
    return args


class CommandCompletion(Logging):
    """Perform system command completion
    """

    @print_exc
    def __call__(self, text):
        self.log('completecommands\t\t%r', text)
        matches = []
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            matches.append(name)
        self.log('completecommands\t\t%r', matches[:100])
        return matches


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
        process = subprocess.Popen(gnupg_exe+' --list-keys --with-colons',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        for line in stdout.strip().split('\n'):
            if line[:3] == 'pub':
                fields = line.split(':')
                keyid = fields[4]
                userid = fields[9]
                yield (keyid, userid)


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


def main(args=None):
    verbose = False
    if args is None:
        args = sys.argv[1:]
    if args and args[0] == '-v':
        verbose = True
        args = args[1:]

    c = GPGKeys(verbose=verbose)
    if args:
        c.onecmd(' '.join(args))
    else:
        try:
            c.cmdloop()
        except KeyboardInterrupt:
            print
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

