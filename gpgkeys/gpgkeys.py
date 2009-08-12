# gpgkeys
#

import os, sys
import atexit
import subprocess

from datetime import datetime

from escape import split
from escape import get_quote_char

from completion import completer
from completion import completion
from completion import cmd
from completion import readline
from completion import print_exc

gnupg_exe = 'gpg'

GNUPGHOME = os.environ.get('GNUPGHOME', '~/.gnupg')
GNUPGHOME = os.path.abspath(os.path.expanduser(GNUPGHOME))

UMASK = 0077

GLOBAL = []
KEY    = ['--openpgp']
SIGN   = ['--local-user']
CHECK  = [] #'--trusted-key']
LIST   = ['--fingerprint', '--with-colons']
INPUT  = ['--merge-only']
OUTPUT = ['--armor', '--output']
SERVER = ['--keyserver']
EXPERT = ['--expert']


class GPGKeys(cmd.Cmd):

    intro = 'gpgkeys 1.0 (type help for help)\n'
    prompt = 'gpgkeys> '

    doc_header = 'Available commands (type help <topic>):'
    undoc_header = 'Shortcut commands (type help <topic>):'

    def __init__(self, completekey='tab', stdin=None, stdout=None, verbose=False):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self.verbose = verbose
        os.umask(UMASK)

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
        # Make '.' work as shell escape character
        # Make '#' work as comment character
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
        # Automatically expand unique command prefixes
        # https://svn.thomas-lotze.de/repos/public/tl.cli/trunk/tl/cli/_cmd.py
        if name.startswith(('do_', 'complete_', 'help_')):
            matches = set(x for x in self.get_names() if x.startswith(name))
            if len(matches) == 1:
                return getattr(self, matches.pop())
        raise AttributeError(name)

    # Commands

    def preloop(self):
        cmd.Cmd.preloop(self)
        self.init_completer()
        self.init_history()

    def emptyline(self):
        pass

    def default(self, args):
        self.stdout.write('Unknown command (type help for help)\n')

    def do_EOF(self, args):
        """End the session (Usage: ^D)"""
        self.stdout.write('\n')
        return self.do_quit(args)

    def do_quit(self, args):
        """End the session (Usage: quit)"""
        return True # Break the cmd loop

    def do_q(self, args):
        return self.do_quit(args)

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
        args = split(args)
        self.gnupg('--import', *args)

    def do_importsec(self, args):
        """Import secret and public keys from a file (Usage: importsec <filename>)"""
        args = split(args)
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

    def do_lx(self, args):
        self.do_listsec(args)

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
        args = split(args)
        self.gnupg('--recv-keys', *args)

    def do_send(self, args):
        """Send keys to the keyserver (Usage: send <keyspec>)"""
        args = split(args)
        self.gnupg('--send-keys', *args)

    def do_refresh(self, args):
        """Refresh keys from the keyserver (Usage: refresh <keyspec>)"""
        args = split(args)
        self.gnupg('--refresh-keys', *args)

    def do_fetch(self, args):
        """Fetch keys from a URL (Usage: fetch <url>)"""
        args = split(args)
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

    def shell_getdir(self, dir):
        process = subprocess.Popen('cd %s; pwd' % dir,
            shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            for line in stdout.strip().split('\n'):
                return line
        return ''

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
        self.file_completion = FileCompletion(do_log)
        self.completefiles = self.file_completion.complete

        self.system_completion = SystemCompletion()
        self.completesys = self.system_completion.complete

        self.key_completion = KeyCompletion()
        self.completekeys = self.key_completion.complete

        self.keyserver_completion = KeyserverCompletion()
        self.completekeyservers = self.keyserver_completion.complete

    def isoption(self, string):
        # True if 'string' is an option flag
        return string.startswith('-')

    def isfilename(self, string):
        # True if 'string' is a filename
        return (os.sep in string)

    def follows(self, string, line, begidx, deltas_=('"', "'", '')):
        # True if 'string' immediately preceeds the completion
        idx = line.rfind(string, 0, begidx)
        if idx >= 0:
            delta = line[idx+len(string):begidx]
            if delta.strip() in deltas_:
                return True
        return False

    def iscommand(self, line, begidx):
        # True if the completion is a shell command
        delta = line[0:begidx]
        return delta.strip() in ('!', '.', 'shell')

    def ispipe(self, line, begidx):
        # True if the completion is a shell command following a pipe
        return self.follows('|', line, begidx, ('',))

    def isredir(self, line, begidx):
        # True if the completion is anywhere after a shell redirect
        return (line.rfind('|', 0, begidx) >= 0 or
                line.rfind('>', 0, begidx) >= 0 or
                line.rfind('<', 0, begidx) >= 0)

    def basecomplete(self, text, line, begidx, default):
        if self.ispipe(line, begidx):
            if self.isfilename(text):
                return self.completefiles(text)
            return self.completesys(text)
        if self.isredir(line, begidx):
            return self.completefiles(text)
        return default(text)

    def completefiles_(self, text, line, begidx):
        return self.basecomplete(text, line, begidx, self.completefiles)

    def completekeys_(self, text, line, begidx):
        return self.basecomplete(text, line, begidx, self.completekeys)

    def completedefault_(self, text, line, begidx):
        return self.basecomplete(text, line, begidx, self.completedefault)

    def completeoptions(self, text, options):
        return [x for x in options if x.startswith(text)]

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
            return self.completefiles(text)
        return self.completekeys_(text, line, begidx)

    def complete_import(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completefiles_(text, line, begidx)

    def complete_importsec(self, text, line, begidx, endidx):
        options = GLOBAL + INPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        return self.completefiles_(text, line, begidx)

    def complete_export(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefiles(text)
        return self.completekeys_(text, line, begidx)

    def complete_exportsec(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefiles(text)
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

    def complete_lx(self, text, line, begidx, endidx):
        return self.complete_listsec(text, line, begidx, endidx)

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
        return self.completefiles_(text, line, begidx)

    def complete_shell(self, text, line, begidx, endidx):
        # If the user types '. foo' we end up here
        options = GLOBAL
        if self.isoption(text):
            return self.completeoptions(text, options)
        if self.iscommand(line, begidx):
            if not self.isfilename(text):
                return self.completesys(text)
        return self.completefiles_(text, line, begidx)

    def completenames(self, text, *ignored):
        # If the user types '.foo' we end up here and not
        # in complete_shell.
        if self.iscommand(text, 1):
            if not self.isoption(text) and not self.isfilename(text):
                return self.completesys(text)
        return cmd.Cmd.completenames(self, text, *ignored)

    # Help

    shortcuts = {'ls': 'list',
                 'll': 'listsig',
                 'lx': 'listsec',
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
                        # /me covers eyes...
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
        length = 100
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        readline.set_history_length(length)
        atexit.register(readline.write_history_file, histfile)


def splitpipe(args):
    """Split args tuple at first '|' or '>' or '<'.
    """
    pipe = ()
    for i in range(len(args)):
        a = args[i]
        if a and a[0] in '|><':
            pipe = args[i:]
            args = args[:i]
            break
    return args, pipe


class Logging(object):
    """Simple logging for filename completion
    """

    def __init__(self, do_log=False):
        self.do_log = do_log
        self.log_file = os.path.abspath('gpgkeys.log')
        self.log('-----', date=False, scale=False)

    def log(self, format, *args, **kw):
        if not self.do_log:
            return

        now = datetime.now().isoformat()[:19]
        now = '%s %s\t' % (now[:10], now[11:])

        f = open(self.log_file, 'at')
        try:
            if kw.get('date', True):
                f.write(now)
            if kw.get('scale', False):
                f.write('\t\t\t 0123456789012345678901234567890123456789012345678901234567890\n')
                if kw.get('date', True):
                    f.write(now)
            f.write(format % args)
            f.write('\n')
        finally:
            f.close()


class FileCompletion(Logging):
    """Perform filename completion

    Extends readline's default filename quoting by taking
    care of backslash-quoted characters.

    Quote characters are double quote and single quote.
    Prefers double-quote quoting over backslash quoting a la bash.
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
        completer.match_hidden_files = False
        completer.tilde_expansion = False
        self.tilde_expansion = True

        self.quoted = {}
        for c in completer.word_break_characters:
            self.quoted.setdefault(c, '\\'+c)

    @print_exc
    def complete(self, text):
        self.log('completefiles\t\t%r', text)
        if text.startswith('~') and os.sep not in text:
            matches = completion.complete_username(text)
        else:
            matches = completion.complete_filename(text)
        self.log('completefiles\t\t%r', matches[:100])
        return matches

    @print_exc
    def char_is_quoted(self, text, index):
        self.log('char_is_quoted\t\t%r %d', text, index, scale=True)
        qc = get_quote_char(text, index)
        # If a character is preceeded by a backslash, we consider
        # it quoted.
        if (qc != "'" and
            index > 0 and
            text[index-1] == '\\' and
            text[index] in completer.word_break_characters):
            self.log('char_is_quoted\t\tTrue1')
            return True
        # If we have a backslash-quoted character, we must tell
        # readline not to word-break at the backslash.
        if (qc != "'" and
            text[index] == '\\' and
            index+1 < len(text) and
            text[index+1] in completer.word_break_characters):
            self.log('char_is_quoted\t\tTrue2')
            return True
        # If we have an unquoted quote character, we must check
        # whether it is quoted by the other quote character.
        if (index > 0 and
            text[index] in completer.quote_characters):
            if qc in completer.quote_characters and qc != text[index]:
                self.log('char_is_quoted\t\tTrue3')
                return True
        else:
            # If we still have an unquoted character, check if there
            # was an opening quote character.
            if (index > 0 and
                text[index] in completer.word_break_characters):
                if qc in completer.quote_characters:
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
            # except for single quotes.
            if qc == "'":
                text = text.replace("'\\''", "'")
            else:
                for c in completer.word_break_characters:
                    text = text.replace(self.quoted[c], c)
        self.log('dequote_filename\t%r', text)
        return text

    @print_exc
    def quote_filename(self, text, match_type, quote_char):
        self.log('quote_filename\t\t%r %d %r', text, match_type, quote_char)
        if self.tilde_expansion and '~' in text:
            text = completion.expand_tilde(text)
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
            if check and qc != "'" and not quote_char:
                for c in completer.word_break_characters:
                    check = check.replace(self.quoted[c], '')
                if check:
                    for c in completer.word_break_characters:
                        if c in check:
                            break
                    else:
                        check = ''
            # Add leading and trailing quote characters
            if check:
                if match_type == completer.SINGLE_MATCH:
                    if not os.path.isdir(text):
                        text = text + qc
                text = qc + text
        self.log('quote_filename\t\t%r', text)
        return text


class SystemCompletion(object):
    """Perform system command completion
    """

    @print_exc
    def complete(self, text):
        prefix = ''
        if text.startswith(('!', '.')): # XXX
            prefix = text[0]
            text = text[1:]
        return [prefix+x for x in self.read_path() if x.startswith(text)]

    def read_path(self):
        path = os.environ.get('PATH')
        dirs = path.split(':')
        for dir in dirs:
            for file in os.listdir(dir):
                if os.access(os.path.join(dir, file), os.R_OK|os.X_OK):
                    yield file


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
    def complete(self, text, keyids_only=True):
        self.update_keys()

        keyid = text.upper()
        matches = [x for x in self.keyspecs.iterkeys() if x.startswith(keyid)]
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

            for keyid, userid in self.read_pubkeys():
                keyid = keyid[8:]
                info = (keyid, userid)
                append('%s %s' % info, info)
            self.mtimes = mtimes
            self.keyspecs = keyspecs

    def read_pubkeys(self):
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
    in ~/.gpg.conf.
    """

    def __init__(self):
        self.gpgconf = os.path.join(GNUPGHOME, 'gpg.conf')
        self.mtime = 0
        self.servers = []

    @print_exc
    def complete(self, text):
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

