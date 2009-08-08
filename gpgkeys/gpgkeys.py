#!/usr/bin/env /usr/local/python2.6/bin/python

# gpgkeys 1.0
#

# TODO:
# - filename completion should handle names with spaces
# - implement command aliases

import os, sys
import readline
import atexit
import subprocess

from datetime import datetime

from escape import escape
from escape import unescape
from escape import split
from escape import get_quote_char

from completion import completer
from completion import completion
from completion import cmd
from completion import print_exc

gnupg_exe = 'gpg'

UMASK = 0077

GLOBAL = []
KEY    = ['--openpgp']
SIGN   = ['--local-user']
CHECK  = ['--trusted-key']
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

    def shell_ls(self, *args):
        self.system('ls -F', *[escape(unescape(x)) for x in args])

    def shell_ll(self, *args):
        self.system('ls -lF', *[escape(unescape(x)) for x in args])

    def shell_chdir(self, *args):
        if args:
            dir = args[0]
        else:
            dir = os.path.expanduser('~')
        try:
            os.chdir(unescape(dir))
        except OSError, e:
            self.stdout.write('%s\n' % (e,))

    def shell_umask(self, *args):
        if args:
            try:
                mask = int(args[0], 8)
            except ValueError, e:
                self.stdout.write('%s\n' % (e,))
                return
            if mask < 512:
                os.umask(mask)
        try:
            self.system('umask', *args)
        except OSError, e:
            self.stdout.write('%s\n' % (e,))

    def shell_default(self, *args):
        self.system(args[0], *[escape(unescape(x)) for x in args[1:]])

    def parseline(self, line):
        # Make '.' work as shell escape character
        # Make '#' work as comment character
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!' or line[0] == '.': # Allow '.'
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        elif line[0] == '#': # Allow comments
            line = ''
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars:
            i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def __getattr__(self, name):
        # Automatically expand unique command prefixes
        # Thanks to Thomas Lotze
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
        # Pass to GnuPG as is
        args = split(args)
        self.gnupg(*args)

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
        return self.do_list(args)

    def do_listsec(self, args):
        """List secret keys (Usage: listsec <keyspec>)"""
        args = split(args)
        self.gnupg('--list-secret-keys', *args)

    def do_lx(self, args):
        return self.do_listsec(args)

    def do_listsig(self, args):
        """List public keys including signatures (Usage: listsig <keyspec>)"""
        args = split(args)
        self.gnupg('--list-sigs', *args)

    def do_ll(self, args):
        return self.do_listsig(args)

    def do_checksig(self, args):
        """Like listsig, but also verify the signatures (Usage: checksig <keyspec>)"""
        args = split(args)
        self.gnupg('--check-sigs', *args)

    def do_edit(self, args):
        """Enter the key edit menu (Usage: edit <keyspec>)"""
        args = split(args)
        self.gnupg('--edit-key', *args)

    def do_e(self, args):
        return self.do_edit(args)

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
        args, pipe = splitpipe(*split(args))
        args = ('--export',) + args + ('|', gnupg_exe, '--list-packets') + pipe
        self.gnupg(*args)

    def do_dumpsec(self, args):
        """Dump packet sequence of a secret key (Usage: dumpsec <keyspec>)"""
        args, pipe = splitpipe(*split(args))
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

    # Completions

    def init_completer(self):
        self.file_completion = FileCompletion()
        self.completefiles = self.file_completion.complete

        self.system_completion = SystemCompletion()
        self.completesys = self.system_completion.complete

        self.key_completion = KeyCompletion()
        self.completekeys = self.key_completion.complete

    def completeoptions(self, text, options):
        return [x for x in sorted(options) if x.startswith(text)]

    def iscommand(self, line, begidx):
        delta = line[0:begidx].strip()
        return delta in ('!', '.', 'shell')

    def follows(self, text, line, begidx):
        text = text + ' '
        textidx = line.find(text)
        if 0 <= textidx:
            end = textidx+len(text)
            delta = text[end:begidx]
            if not delta.strip():
                return True
        return False

    def complete_genkey(self, text, *ignored):
        options = GLOBAL + KEY + EXPERT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return []

    def complete_genrevoke(self, text, line, begidx, endidx):
        options = GLOBAL + KEY + OUTPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefiles(text)
        else:
            return self.completekeys(text)

    def complete_import(self, text, *ignored):
        options = GLOBAL + INPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completefiles(text)

    def complete_importsec(self, text, *ignored):
        options = GLOBAL + INPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completefiles(text)

    def complete_export(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefiles(text)
        else:
            return self.completekeys(text)

    def complete_exportsec(self, text, line, begidx, endidx):
        options = GLOBAL + OUTPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        if self.follows('--output', line, begidx):
            return self.completefiles(text)
        else:
            return self.completekeys(text)

    def complete_list(self, text, *ignored):
        options = GLOBAL + LIST
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_ls(self, text, *ignored):
        return self.complete_list(text)

    def complete_listsec(self, text, *ignored):
        options = GLOBAL + LIST
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_lx(self, text, *ignored):
        return self.complete_listsec(text)

    def complete_listsig(self, text, *ignored):
        options = GLOBAL + LIST
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_ll(self, text, *ignored):
        return self.complete_listsig(text)

    def complete_checksig(self, text, *ignored):
        options = GLOBAL + LIST + CHECK
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_edit(self, text, *ignored):
        options = GLOBAL + KEY + SIGN + EXPERT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text, keyids_only=True) # XXX

    def complete_e(self, text, *ignored):
        return self.complete_edit(text)

    def complete_lsign(self, text, *ignored):
        options = GLOBAL + KEY + SIGN
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text, keyids_only=True) # XXX

    def complete_sign(self, text, *ignored):
        options = GLOBAL + KEY + SIGN
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text, keyids_only=True) # XXX

    def complete_del(self, text, *ignored):
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_delsec(self, text, *ignored):
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_delsecpub(self, text, *ignored):
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_search(self, text, *ignored):
        options = GLOBAL + SERVER
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text, keyids_only=True) # XXX

    def complete_recv(self, text, *ignored):
        options = GLOBAL + SERVER + INPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text, keyids_only=True) # XXX

    def complete_send(self, text, *ignored):
        options = GLOBAL + SERVER
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_refresh(self, text, *ignored):
        options = GLOBAL + SERVER + INPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_fetch(self, text, *ignored):
        options = GLOBAL + INPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return []

    def complete_dump(self, text, *ignored):
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_dumpsec(self, text, *ignored):
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_fdump(self, text, *ignored):
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completefiles(text)

    def complete_shell(self, text, line, begidx, endidx):
        # If the user types '. foo' we end up here
        options = GLOBAL
        if text.startswith('-'):
            return self.completeoptions(text, options)
        if self.iscommand(line, begidx):
            return self.completesys(text)
        return self.completefiles(text)

    def completenames(self, text, *ignored):
        # XXX If the user types '.foo' we end up here and not in complete_shell
        if self.iscommand(text, 1):
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


def splitpipe(*args):
    """Split args tuple at first '|' or '>' or '>>'.
    """
    pipe = ()
    for i in range(len(args)):
        a = args[i]
        if a and (a[0] == '|' or a[0] == '>'):
            pipe = args[i:]
            args = args[:i]
            break
    return args, pipe


class Logging(object):
    """Very simple logging for filename completion
    """

    def __init__(self, nolog=False):
        self.nolog = nolog
        self.log('-----', nodate=True)

    @print_exc
    def log(self, format, *args, **kw):
        if self.nolog:
            return

        now = datetime.now().isoformat()[:19]
        now = '%s %s\t' % (now[:10], now[11:])

        f = open('/Users/stefan/PGP2004/gpgkeys.log', 'at')
        try:
            if not kw.get('nodate', False):
                f.write(now)
            f.write(format % args)
            f.write('\n')
        finally:
            f.flush()
            f.close()


class FileCompletion(Logging):
    """Perform filename completion

    Extends readline's default filename quoting by taking
    care of backslash-quoted characters.
    """

    @print_exc
    def __init__(self):
        Logging.__init__(self)
        completer.quote_characters = '"\''
        completer.word_break_characters = ' \t\n"\'`><=;|&\\'
        completer.char_is_quoted_function = self.char_is_quoted
        completer.filename_quote_characters = ' \t\n"\'\\'
        completer.filename_dequoting_function = self.dequote_filename
        completer.filename_quoting_function = self.quote_filename
        completer.match_hidden_files = False
        completer.tilde_expansion = False
        self.tilde_expansion = True

        self.quoted = {'"': '\\"', "'": "'\\''"}
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
        self.log('char_is_quoted\t\t%r %d', text, index)
        # If a character is preceeded by a backslash, we consider
        # it quoted.
        if (index > 0 and
            text[index-1] == '\\' and
            text[index] in completer.word_break_characters):
            self.log('char_is_quoted\t\tTrue1')
            return True
        # If we have a backslash-quoted character, we must tell
        # readline not to word-break at the backslash.
        if (text[index] == '\\' and
            index+1 < len(text) and
            text[index+1] in completer.word_break_characters):
            self.log('char_is_quoted\t\tTrue2')
            return True
        # If we have an unquoted quote character, we must check
        # whether it is quoted by the other quote character.
        if (index > 0 and
            text[index] in completer.quote_characters):
            qc = get_quote_char(text, index)
            if qc in completer.quote_characters and qc != text[index]:
                self.log('char_is_quoted\t\tTrue3')
                return True
        else:
            # If we still have an unquoted character, check if there is
            # an opening quote character somewhere.
            if (index > 0 and
                text[index] in completer.word_break_characters):
                qc = get_quote_char(text, index)
                if qc in completer.quote_characters:
                    self.log('char_is_quoted\t\tTrue4')
                    return True
        self.log('char_is_quoted\t\tFalse')
        return False

    @print_exc
    def dequote_filename(self, text, quote_char):
        self.log('dequote_filename\t%r %r', text, quote_char)
        if len(text) > 1:
            qc = quote_char or completer.preferred_quote_character
            # Don't backslash-dequote backslashes between single quotes
            word_break_characters = completer.word_break_characters
            if qc == "'":
                word_break_characters = word_break_characters[:-1]
            for c in word_break_characters:
                text = text.replace(self.quoted[c], c)
        self.log('dequote_filename\t%r', text)
        return text

    @print_exc
    def quote_filename(self, text, match_type, quote_char):
        self.log('quote_filename\t\t%r %d %r', text, match_type, quote_char)
        if self.tilde_expansion and '~' in text:
            text = completion.expand_tilde(text)
        if text:
            qc = quote_char or completer.preferred_quote_character
            # Don't backslash-quote backslashes between single quotes
            if qc != "'":
                text = text.replace('\\', self.quoted['\\'])
            text = text.replace(qc, self.quoted[qc])
            check = text
            if not quote_char:
                # Don't quote strings if all characters are already
                # backslash-quoted
                for c in completer.word_break_characters:
                    check = check.replace(self.quoted[c], '')
                if check:
                    for c in completer.word_break_characters:
                        if c in check:
                            break
                    else:
                        check = ''
            if check:
                # Add leading and trailing quote characters
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

    @print_exc
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

    @print_exc
    def __init__(self):
        home = os.environ.get('GNUPGHOME', '~/.gnupg')
        home = os.path.expanduser(home)
        self.pubring = os.path.join(home, 'pubring.gpg')
        self.secring = os.path.join(home, 'secring.gpg')
        self.mtimes = (0, 0)
        self.keyspecs = {}

    @print_exc
    def complete(self, text, keyids_only=False):
        self.update_keys()

        keyid = text.upper()
        matches = [x for x in self.keyspecs.iterkeys() if x.startswith(keyid)]
        if len(matches) == 1:
            if keyids_only:
                return [x[0] for x in self.keyspecs[matches[0]]]
            else:
                return ['%s "%s"' % x for x in self.keyspecs[matches[0]]]
        return matches

    @print_exc
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

    @print_exc
    def read_pubkeys(self):
        process = subprocess.Popen(gnupg_exe+' --list-keys --with-colons',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        for line in stdout.rstrip().split('\n'):
            if line[:3] == 'pub':
                fields = line.split(':')
                keyid = fields[4]
                userid = fields[9]
                yield (keyid, userid)


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

