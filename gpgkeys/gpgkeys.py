# gpgkeys
#

import os
import sys
import cmd
import atexit
import getopt
import subprocess
import splitter

from rl import completer
from rl import completion
from rl import history
from rl import readline
from rl import print_exc

from splitter import scan_unquoted
from splitter import rscan_unquoted
from splitter import splitpipe
from splitter import closequote

from completions.filename import FilenameCompletion
from completions.command import CommandCompletion
from completions.key import KeyCompletion
from completions.keyserver import KeyserverCompletion

from config import GNUPGEXE
from config import UMASK
from config import LOGGING

GLOBAL = []
KEY    = ['--openpgp']
SIGN   = ['--local-user']
CHECK  = [] #['--trusted-key']
LIST   = ['--fingerprint', '--with-colons']
INPUT  = ['--merge-only']
OUTPUT = ['--armor', '--output']
SERVER = ['--keyserver']
EXPERT = ['--expert']
SECRET = ['--secret']
ALL    = ['--all']


def split(args):
    # Always apply closequote transform
    return closequote(splitter.split(args))


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

    def emptyline(self):
        pass

    def default(self, args):
        """Unknown command"""
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
        """Import keys from a file (Usage: import <filename>)"""
        mine, rest = splitpipe(split(args))
        args = ('--import',)
        if '--secret' in mine:
            args = ('--import', '--allow-secret-key')
            mine = tuple(x for x in mine if x != '--secret')
        args = args + fixmergeonly(mine) + rest
        self.gnupg(*args)

    def do_export(self, args):
        """Export keys to stdout or to a file (Usage: export <keyspec>)"""
        mine, rest = splitpipe(split(args))
        args = ('--export',)
        if '--secret' in mine:
            args = ('--export-secret-keys',)
            mine = tuple(x for x in mine if x != '--secret')
        args = args + mine + rest
        self.gnupg(*args)

    def do_list(self, args):
        """List keys (Usage: list <keyspec>)"""
        mine, rest = splitpipe(split(args))
        args = ('--list-keys',)
        if '--secret' in mine:
            args = ('--list-secret-keys',)
            mine = tuple(x for x in mine if x != '--secret')
        args = args + mine + rest
        self.gnupg(*args)

    def do_ls(self, args):
        self.do_list(args)

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
        """Delete a key from the keyring (Usage: del <keyspec>)"""
        mine, rest = splitpipe(split(args))
        args = ('--delete-key',)
        if '--secret' in mine:
            args = ('--delete-secret-key',)
            mine = tuple(x for x in mine if x != '--secret')
        if '--all' in mine:
            args = ('--delete-secret-and-public-key',)
            mine = tuple(x for x in mine if x != '--all')
        args = args + mine + rest
        self.gnupg(*args)

    def do_search(self, args):
        """Search for keys on a keyserver (Usage: search <keyspec>)"""
        args = split(args)
        self.gnupg('--search-keys', *args)

    def do_recv(self, args):
        """Fetch keys from a keyserver (Usage: recv <keyids>)"""
        args = fixmergeonly(split(args))
        self.gnupg('--recv-keys', *args)

    def do_send(self, args):
        """Send keys to a keyserver (Usage: send <keyspec>)"""
        args = split(args)
        self.gnupg('--send-keys', *args)

    def do_refresh(self, args):
        """Refresh keys from a keyserver (Usage: refresh <keyspec>)"""
        args = fixmergeonly(split(args))
        self.gnupg('--refresh-keys', *args)

    def do_fetch(self, args):
        """Fetch keys from a URL (Usage: fetch <url>)"""
        args = fixmergeonly(split(args))
        self.gnupg('--fetch-keys', *args)

    def do_dump(self, args):
        """List the packet sequence of a key (Usage: dump <keyspec>)"""
        mine, rest = splitpipe(split(args))
        args = ('--export',)
        if '--secret' in mine:
            args = ('--export-secret-keys',)
            mine = tuple(x for x in mine if x != '--secret')
        args = args + mine + ('|', GNUPGEXE, '--list-packets') + rest
        self.gnupg(*args)

    def do_fdump(self, args):
        """List the packet sequence of a key stored in a file (Usage: fdump <filename>)"""
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

    def shell_getdir(self, dir):
        process = subprocess.Popen('cd %s; pwd' % dir,
            shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            for line in stdout.strip().split('\n'):
                return line

    def shell_ls(self, *args):
        self.system('ls', '-F', *args)

    def shell_ll(self, *args):
        self.system('ls', '-lF', *args)

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
        self.completefilename = FilenameCompletion(do_log=do_log)
        self.completecommand = CommandCompletion(do_log=do_log)
        self.completekeyid = KeyCompletion()
        self.completekeyserver = KeyserverCompletion()
        completer.word_break_hook = self.word_break_hook
        completer.display_matches_hook = self.display_matches_hook

    def isoption(self, text):
        # True if 'text' is an option flag
        return text.startswith('-')

    def isfilename(self, text):
        # True if 'text' is a filename
        return text.startswith('~') or (os.sep in text)

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

    def pipepos(self, line, begidx):
        # True if the completion follows a pipe or semicolon
        idx = rscan_unquoted(line, begidx, ('|', ';'))
        if idx >= 0:
            delta = line[idx+1:begidx]
            if delta.strip() in ('"', "'", ''):
                # '>|' is not a pipe but an output redirect
                if idx > 0 and line[idx] == '|':
                    if rscan_unquoted(line, begidx, ('>',)) == idx-1:
                        return False
                return True
        return False

    def postredir(self, line, begidx):
        # True if the completion is anywhere after a shell redirect
        return scan_unquoted(line, begidx, ('|', '>', '<')) >= 0

    def basecomplete(self, default, text, line, begidx):
        if self.pipepos(line, begidx):
            if not self.isfilename(text):
                return self.completecommand(text)
            return self.completefilename(text)
        if self.postredir(line, begidx):
            return self.completefilename(text)
        return default(text)

    def completeoption(self, text, options):
        return [x for x in options if x.startswith(text)]

    # Completion grid

    def complete_genkey(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + EXPERT
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completedefault, text, line, begidx)

    def complete_genrevoke(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + OUTPUT
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--output', line, begidx):
            return self.completefilename(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_import(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT + SECRET
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completefilename, text, line, begidx)

    def complete_export(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT + SECRET
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--output', line, begidx):
            return self.completefilename(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_list(self, text, line, begidx, endidx):
        options = GLOBAL + LIST + SECRET
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_ls(self, text, line, begidx, endidx):
        return self.complete_list(text, line, begidx, endidx)

    def complete_listsig(self, text, line, begidx, endidx):
        options = GLOBAL + LIST
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_ll(self, text, line, begidx, endidx):
        return self.complete_listsig(text, line, begidx, endidx)

    def complete_checksig(self, text, line, begidx, endidx):
        options = GLOBAL + LIST + CHECK
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_edit(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + SIGN + EXPERT
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--local-user', line, begidx):
            return self.completekeyid(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_e(self, text, line, begidx, endidx):
        return self.complete_edit(text, line, begidx, endidx)

    def complete_lsign(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + SIGN
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--local-user', line, begidx):
            return self.completekeyid(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_sign(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + SIGN
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--local-user', line, begidx):
            return self.completekeyid(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_del(self, text, line, begidx, endidx):
        options = GLOBAL + SECRET + ALL
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_search(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyserver(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_recv(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER + INPUT
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyserver(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_send(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyserver(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_refresh(self, text, line, begidx, endidx):
        options = GLOBAL + SERVER + INPUT
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.follows('--keyserver', line, begidx):
            return self.completekeyserver(text)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_fetch(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completedefault, text, line, begidx)

    def complete_dump(self, text, line, begidx, endidx):
        options = GLOBAL + SECRET
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completekeyid, text, line, begidx)

    def complete_fdump(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoption(text, options)
        return self.basecomplete(self.completefilename, text, line, begidx)

    def complete_shell(self, text, line, begidx, endidx):
        options = GLOBAL
        if self.isoption(text):
            return self.completeoption(text, options)
        if self.commandpos(line, begidx):
            if not self.isfilename(text):
                return self.completecommand(text)
        return self.basecomplete(self.completefilename, text, line, begidx)

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
        if num_matches > completer.query_items > 0:
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

    # Help

    shortcuts = {'ls': 'list',
                 'll': 'listsig',
                 'e':  'edit'}

    def expandshortcut(self, arg):
        return self.shortcuts.get(arg, arg)

    def do_help(self, arg):
        """Interactive help (Usage: help <topic>)"""
        if arg:
            arg = self.expandshortcut(arg)
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
                            options = compfunc('-', '', 0, 0)

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
        histfile = os.path.expanduser('~/.gpgkeys_history')
        history.read_file(histfile)
        history.length = 100
        atexit.register(history.write_file, histfile)


def fixmergeonly(args):
    # gpg: WARNING: "--merge-only" is a deprecated option
    # gpg: please use "--import-options merge-only" instead
    for i in range(len(args)):
        a = args[i]
        if a == '--merge-only':
            args = args[:i] + ('--import-options', 'merge-only') + args[i+1:]
            break
    return args


def main(args=None):
    verbose = False

    if args is None:
        args = sys.argv[1:]

    try:
        options, args = getopt.getopt(args, 'hv', ('help', 'verbose'))
    except getopt.GetoptError, e:
        print >>sys.stderr, 'gpgkeys:', e
        return 1

    for name, value in options:
        if name in ('-v', '--verbose'):
            verbose = True
        if name in ('-h', '--help'):
            print "Type 'gpgkeys' to start the gpgkeys shell"
            return 0

    shell = GPGKeys(verbose=verbose)
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

