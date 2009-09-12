# gpgkeys
#

import os
import sys
import cmd
import atexit
import subprocess

from datetime import datetime

from escape import scan_open_quote
from escape import split

from rl import completer
from rl import completion
from rl import history
from rl import print_exc

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
        self.completefilenames = BashFilenameCompletion(do_log)
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
        return (os.sep in text or '~' in text)

    def follows(self, text, line, begidx):
        # True if 'text' immediately precedes the completion
        idx = line.rfind(text, 0, begidx)
        if idx >= 0:
            delta = line[idx+len(text):begidx]
            return delta.strip() in ('"', "'", '')
        return False

    def iscommand(self, line, begidx):
        # True if the completion is a shell command at position 0
        delta = line[0:begidx]
        return delta.strip() in ('!', '.', 'shell')

    def postpipe(self, line, begidx):
        # True if the completion is a shell command following
        # a pipe or semicolon
        delta = line[0:begidx]
        return delta.strip()[-1:] in ('|', ';')

    def postredir(self, line, begidx):
        # True if the completion happens anywhere after a shell
        # redirect
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
        if self.iscommand(line, begidx):
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
        if line[0] in ('!', '.'):
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
                 'e':  'edit',
                 'q':  'quit'}

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


class Logging(object):
    """Simple logging for filename completion
    """

    def __init__(self, do_log=False):
        self.do_log = do_log
        self.log_file = os.path.abspath('gpgkeys.log')

    def log(self, format, *args, **kw):
        if not self.do_log:
            return

        now = datetime.now().isoformat()[:19]
        now = '%s %s\t' % (now[:10], now[11:])

        f = open(self.log_file, 'at')
        try:
            f.write(now)
            if kw.get('ruler', False):
                f.write('\t\t\t 0123456789012345678901234567890123456789012345678901234567890\n')
                f.write(now)
            f.write(format % args)
            f.write('\n')
        finally:
            f.close()


class FilenameCompletion(Logging):
    """Perform filename completion

    Extends readline's default filename quoting by taking
    care of backslash-quoted characters.

    Quote characters are double quote and single quote.
    Prefers double-quote quoting over backslash quoting.
    Word break characters are quoted with backslashes when needed.
    Backslash quoting is disabled between single quotes.
    """

    def __init__(self, do_log=False):
        Logging.__init__(self, do_log)
        completer.quote_characters = '"\''
        completer.word_break_characters = '\\ \t\n"\'`><=;|&'
        completer.char_is_quoted_function = self.char_is_quoted
        completer.filename_quote_characters = '\\ \t\n"\''
        completer.filename_quoting_function = self.quote_filename
        completer.filename_dequoting_function = self.dequote_filename
        completer.directory_completion_hook = self.dequote_dirname
        completer.match_hidden_files = False
        completer.tilde_expansion = True
        self.quoted = dict((x, '\\'+x) for x in completer.word_break_characters)
        self.log('-----')

    @print_exc
    def __call__(self, text):
        self.log('completefilenames\t%r', text)
        if text.startswith('~') and (os.sep not in text):
            matches = completion.complete_username(text)
        else:
            matches = completion.complete_filename(text)
        self.log('completefilenames\t%r', matches[:100])
        return matches

    @print_exc
    def char_is_quoted(self, text, index):
        qc = scan_open_quote(text, index)
        self.log('char_is_quoted\t\t%r %d %r', text, index, qc, ruler=True)
        # If a character is preceded by a backslash, we consider
        # it quoted.
        if (qc != "'" and index > 0 and text[index-1] == '\\' and
            text[index] in completer.word_break_characters):
            self.log('char_is_quoted\t\tTrue1')
            return True
        # If we have a backslash-quoted character, we must tell
        # readline not to word-break at the backslash either.
        if (qc != "'" and text[index] == '\\' and index+1 < len(text) and
            text[index+1] in completer.word_break_characters):
            self.log('char_is_quoted\t\tTrue2')
            return True
        # If we have an unquoted quote character, check whether
        # it is quoted by the other quote character.
        if index > 0 and text[index] in completer.quote_characters:
            if qc and qc in completer.quote_characters and qc != text[index]:
                self.log('char_is_quoted\t\tTrue3')
                return True
        else:
            # If we still have an unquoted character, check whether
            # there is an open quote character.
            if index > 0 and text[index] in completer.word_break_characters:
                if qc and qc in completer.quote_characters:
                    self.log('char_is_quoted\t\tTrue4')
                    return True
        self.log('char_is_quoted\t\tFalse')
        return False

    @print_exc
    def dequote_filename(self, text, quote_char):
        self.log('dequote_filename\t%r %r', text, quote_char)
        if len(text) > 1:
            qc = quote_char or completer.quote_characters[0]
            # Don't backslash-dequote characters between single quotes,
            # except single quotes.
            if qc == "'":
                text = text.replace("'\\''", "'")
            else:
                for c in completer.word_break_characters:
                    if self.quoted[c] in text:
                        text = text.replace(self.quoted[c], c)
        self.log('dequote_filename\t%r', text)
        return text

    @print_exc
    def dequote_dirname(self, text):
        self.log("dequote_dirname\t\t%r %r", text, completion.quote_character)
        saved, self.do_log = self.do_log, False
        text = self.dequote_filename(text, completion.quote_character)
        self.do_log = saved
        self.log('dequote_dirname\t\t%r', text)
        return text

    @print_exc
    def quote_filename(self, text, single_match, quote_char):
        self.log('quote_filename\t\t%r %s %r', text, single_match, quote_char)
        if text:
            qc = quote_char or completer.quote_characters[0]
            # Don't backslash-quote backslashes between single quotes
            if qc == "'":
                text = text.replace("'", "'\\''")
            else:
                text = text.replace('\\', self.quoted['\\'])
                text = text.replace(qc, self.quoted[qc])
            check = text
            # Don't quote strings if all characters are already
            # backslash-quoted.
            if qc != "'" and check and not quote_char:
                for c in completer.word_break_characters:
                    if self.quoted[c] in check:
                        check = check.replace(self.quoted[c], '')
                if check:
                    for c in completer.word_break_characters:
                        if c in check:
                            break
                    else:
                        check = ''
            # Add leading and trailing quote characters
            if check:
                if (single_match and not os.path.isdir(text) and
                    not completion.suppress_quote):
                    text = text + qc
                text = qc + text
        self.log('quote_filename\t\t%r', text)
        return text


class BashFilenameCompletion(FilenameCompletion):
    """Perform filename completion

    Prefers backslash quoting a la bash.
    """

    def __init__(self, do_log=False):
        FilenameCompletion.__init__(self, do_log)
        completer.filename_quote_characters = completer.word_break_characters

    @print_exc
    def quote_filename(self, text, single_match, quote_char):
        # If the user has typed a quote character use it
        if quote_char and quote_char in completer.quote_characters:
            return FilenameCompletion.quote_filename(self, text, single_match, quote_char)
        # If not, default to backslash quoting
        self.log('quote_filename\t\t%r %s %r', text, single_match, quote_char)
        if text:
            for c in completer.word_break_characters:
                if c in text:
                    text = text.replace(c, self.quoted[c])
        self.log('quote_filename\t\t%r', text)
        return text


class CommandCompletion(Logging):
    """Perform system command completion
    """

    def __init__(self, do_log=False):
        Logging.__init__(self, do_log)

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

