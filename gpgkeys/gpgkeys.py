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

from escape import split

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

    def getpwd(self, *args):
        dir = ' '.join(args)
        process = subprocess.Popen('cd %s; pwd' % dir,
            shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            for line in stdout.rstrip().split('\n'):
                return line
        return ''

    def gnupg(self, *args):
        return self.system(gnupg_exe, *args)

    def umask(self, *args):
        if args:
            mask = int(args[0], 8)
            if mask < 512:
                os.umask(mask)
        self.system('umask', *args)

    def chdir(self, *args):
        if args:
            dir = self.getpwd(args[0]) # XXX Use dequote here
            if dir:
                os.chdir(dir)
        else:
            os.chdir(os.environ.get('HOME'))

    def __getattr__(self, name):
        # Automatically expand unique command prefixes.
        # Thanks to Thomas Lotze.
        if name.startswith(('do_', 'complete_', 'help_')):
            matches = set(x for x in self.get_names() if x.startswith(name))
            if len(matches) == 1:
                return getattr(self, matches.pop())
        raise AttributeError(name)

    # Commands

    def preloop(self):
        cmd.Cmd.preloop(self)
        os.umask(UMASK)
        self.init_history()
        self.init_completer()

    def emptyline(self):
        pass

    def default(self, args):
        args = split(args)
        self.gnupg(*args)

    def do_EOF(self, args):
        """End the session (Usage: ^D)"""
        self.stdout.write('\n')
        return self.do_quit(args)

    def do_quit(self, args):
        """End the session (Usage: quit)"""
        return True # Break the loop

    def do_q(self, args):
        return self.do_quit(args)

    def do_clear(self, args):
        """Clear the terminal screen (Usage: clear)"""
        self.system('clear')

    def do_genkey(self, args):
        """Generate a new key pair (Usage: genkey)"""
        args = split(args)
        self.gnupg('--gen-key', *args)
        self.update_keyspecs()

    def do_genrevoke(self, args):
        """Generate a revocation certificate for a key (Usage: genrevoke <keyspec>)"""
        args = split(args)
        self.gnupg('--gen-revoke', *args)

    def do_import(self, args):
        """Import public keys from a file (Usage: import <filename>)"""
        args = split(args)
        self.gnupg('--import', *args)
        self.update_keyspecs()

    def do_importsec(self, args):
        """Import secret and public keys from a file (Usage: importsec <filename>)"""
        args = split(args)
        self.gnupg('--import --allow-secret-key', *args)
        self.update_keyspecs()

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
        self.update_keyspecs()

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
        self.update_keyspecs()

    def do_delsec(self, args):
        """Delete a secret key (Usage: delsec <keyspec>)"""
        args = split(args)
        self.gnupg('--delete-secret-key', *args)
        self.update_keyspecs()

    def do_delsecpub(self, args):
        """Delete both secret and public keys (Usage: delsecpub <keyspec>)"""
        args = split(args)
        self.gnupg('--delete-secret-and-public-key', *args)
        self.update_keyspecs()

    def do_search(self, args):
        """Search for keys on the keyserver (Usage: search <keyspec>)"""
        args = split(args)
        self.gnupg('--search-keys', *args)

    def do_recv(self, args):
        """Fetch keys from the keyserver (Usage: recv <keyids>)"""
        args = split(args)
        self.gnupg('--recv-keys', *args)
        self.update_keyspecs()

    def do_send(self, args):
        """Send keys to the keyserver (Usage: send <keyspec>)"""
        args = split(args)
        self.gnupg('--send-keys', *args)

    def do_refresh(self, args):
        """Refresh keys from the keyserver (Usage: refresh <keyspec>)"""
        args = split(args)
        self.gnupg('--refresh-keys', *args)

    def do_dump(self, args):
        """Dump packet sequence of a public key (Usage: dump <keyspec>)"""
        args, pipe = self.splitpipe(*split(args))
        args = ('--export',) + args + ('|', gnupg_exe, '--list-packets') + pipe
        self.gnupg(*args)

    def do_dumpsec(self, args):
        """Dump packet sequence of a secret key (Usage: dumpsec <keyspec>)"""
        args, pipe = self.splitpipe(*split(args))
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
                self.system('ls -F', *args[1:])
            elif cmd == 'll':
                self.system('ls -lF', *args[1:])
            elif cmd == 'cd':
                self.chdir(*args[1:])
            elif cmd == 'umask':
                self.umask(*args[1:])
            else:
                self.system(*args)
        else:
            self.system(os.environ.get('SHELL'))
        self.update_keyspecs()

    def parseline(self, line):
        # Makes . work as shell escape character
        # Makes # work for comments
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!' or line[0] == '.':    # allow '.'
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        elif line[0] == '#':        # allow comments
            line = ''
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars:
            i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def splitpipe(self, *args):
        # Splits args tuple at first '|' or '>' or '>>'
        pipe = ()
        for i in range(len(args)):
            a = args[i]
            if a and (a[0] == '|' or a[0] == '>'):
                pipe = args[i:]
                args = args[:i]
                break
        return args, pipe

    # Completions

    def init_completer(self):
        self.gnureadline_default_delims = " \t\n\"\\'`@$><=;|&{("
        completer.word_break_characters = " \t\n\"\\'`><=;|&{("
        completer.quote_characters = '"\''
        completer.filename_quote_characters = ' \t\n"\''
        completer.filename_quoting_function = self.quote_filename
        completer.filename_dequoting_function = self.dequote_filename
        self.quoted = {'"': '\\"', "'": "'\\''"}
        self.update_keyspecs()

    def completeoptions(self, text, options):
        return [x for x in options if x.startswith(text)]

    def completefiles(self, text, *ignored):
        completion.filename_completion_desired = True
        completion.filename_quoting_desired = True
        return completion.filename_completion(text)

    def completekeys(self, text, keyids_only=False):
        keyid = text.upper()
        matches = [x for x in self.keyspecs.iterkeys() if x.startswith(keyid)]
        if len(matches) == 1:
            if keyids_only:
                return [x[0] for x in self.keyspecs[matches[0]]]
            else:
                return ['%s "%s"' % x for x in self.keyspecs[matches[0]]]
        return matches

    def quote_filename(self, text, match_type, quote_char):
        if text:
            quote_char = quote_char or '"'
            text = text.replace(quote_char, self.quoted[quote_char])
            if match_type == completion.SINGLE_MATCH:
                if not os.path.isdir(text):
                    text = text + quote_char
            text = quote_char + text
        return text

    def dequote_filename(self, text, quote_char):
        if text:
            quote_char = quote_char or '"'
            text = text.replace(self.quoted[quote_char], quote_char)
            if text[0] == quote_char:
                text = text[1:]
            if text[-1] == quote_char:
                text = text[:-1]
        return text

    def update_keyspecs(self):
        keyspecs = {}
        def append(key, value):
            if key in keyspecs:
                keyspecs[key].append(value)
            else:
                keyspecs[key] = [value]
        for keyid, userid in self.read_pubkeys():
            keyid = keyid[8:]
            info = keyid, userid
            append('%s %s' % info, info)
        self.keyspecs = keyspecs

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
        options = GLOBAL + SERVER # + INPUT
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text, keyids_only=True) # XXX

    def complete_send(self, text, *ignored):
        options = GLOBAL + SERVER
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

    def complete_refresh(self, text, *ignored):
        options = GLOBAL + SERVER
        if text.startswith('-'):
            return self.completeoptions(text, options)
        return self.completekeys(text)

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

    def complete_shell(self, text, *ignored):
        if text.startswith('-'):
            return []
        return self.completefiles(text)

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

                        #self.stdout.write("\n")
                        #self.stdout.write("%s\n" % doc)
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
        length = 300
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        readline.set_history_length(length)
        atexit.register(readline.write_history_file, histfile)


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

