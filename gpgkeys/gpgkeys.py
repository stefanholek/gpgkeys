# gpgkeys
#

import locale
locale.setlocale(locale.LC_ALL, '')

import pkg_resources
__version__ = pkg_resources.get_distribution('gpgkeys').version

import os
import sys
import getopt
import signal
import subprocess
import kmd

from parser import splitargs
from parser import parseargs
from parser import parseword

from utils import decode
from utils import ignoresignals

from kmd.completions.filename import FilenameCompletion
from kmd.completions.command import CommandCompletion
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


class GPGKeys(kmd.Kmd):
    """Command line shell for GnuPG.

    Implements a shell providing commands to view and
    manipulate GnuPG keys and keyrings.
    """
    prompt = 'gpgkeys> '
    shell_escape_chars = '!.'
    history_file = '~/.gpgkeys_history'
    history_max_entries = 300

    intro = 'gpgkeys %s (type help for help)\n' % __version__
    nohelp = "gpgkeys: no help on '%s'"
    doc_header = 'Available commands (type help <topic>):'
    alias_header = 'Shortcut commands (type help <topic>):'

    looping = False # True when the cmdloop is active

    def __init__(self, completekey='tab', stdin=None, stdout=None, stderr=None,
                 quote_char='\\', verbose=False):
        super(GPGKeys, self).__init__(completekey, stdin, stdout, stderr)
        self.aliases['e'] = 'edit'
        self.aliases['ls'] = 'list'
        self.aliases['ll'] = 'listsig'
        self.quote_char = quote_char
        self.verbose = verbose
        os.umask(UMASK)

    # Setup custom completions

    def preloop(self):
        super(GPGKeys, self).preloop()
        self.completefilename = FilenameCompletion(self.quote_char)
        self.completecommand = CommandCompletion()
        self.completekeyspec = KeyCompletion()
        self.completekeyserver = KeyserverCompletion()
        self.looping = True

    def postloop(self):
        self.looping = False
        super(GPGKeys, self).postloop()

    # Execute subprocesses

    def popen(self, *args, **kw):
        command = ' '.join(args)
        if self.verbose and kw.get('verbose', False):
            self.stdout.write('gpgkeys: %s\n' % command)
        try:
            process = subprocess.Popen(command,
                shell=True, stdout=kw.get('stdout'), stderr=kw.get('stderr'))
            stdout, stderr = process.communicate()
            return process.returncode, stdout
        except KeyboardInterrupt:
            return 1, None

    def system(self, *args, **kw):
        kw = kw.copy()
        kw.setdefault('verbose', True)
        if self.should_ignore_signals(args):
            with ignoresignals(signal.SIGINT, signal.SIGQUIT):
                return self.popen(*args, **kw)[0]
        else:
            return self.popen(*args, **kw)[0]

    def should_ignore_signals(self, args):
        # XXX: This is crap
        for x in ('less', 'more', 'most', 'view', 'man'):
            if x in args:
                return True

    def gnupg(self, *args):
        return self.system(GNUPGEXE, *args)

    # Available commands

    def emptyline(self):
        """Empty line"""
        pass

    def default(self, args):
        """Unknown command"""
        args = splitargs(args)
        self.stderr.write("gpgkeys: unknown command '%s'\n" % args[0])

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

    def do_version(self, args):
        """Show the GnuPG version (Usage: version)"""
        self.gnupg('--version')

    def do_genkey(self, args):
        """Generate a new key pair and certificate (Usage: genkey)"""
        args = parseargs(args)
        if args.ok:
            self.gnupg('--gen-key', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_genrevoke(self, args):
        """Generate a revocation certificate for a key pair (Usage: genrevoke <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--gen-revoke', *args.tuple)
            else:
                self.do_help('genrevoke')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_import(self, args):
        """Import keys from a file (Usage: import <filename>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--import', *args.tuple)
            elif not self.looping:
                self.gnupg('--import', '-')
            else:
                self.do_help('import')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_export(self, args):
        """Export keys to stdout or to a file (Usage: export [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            command = '--export'
            if args.secret:
                command = '--export-secret-keys'
            self.gnupg(command, *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_list(self, args):
        """List keys (Usage: list [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            command = '--list-keys'
            if args.secret:
                command = '--list-secret-keys'
            self.gnupg(command, *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_listsig(self, args):
        """List keys with signatures (Usage: listsig [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            self.gnupg('--list-sigs', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_checksig(self, args):
        """List keys with signatures and also verify the signatures (Usage: checksig [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            self.gnupg('--check-sigs', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_edit(self, args):
        """Enter the key edit menu (Usage: edit <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--edit-key', *args.tuple)
            else:
                self.do_help('edit')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_lsign(self, args):
        """Sign a key with a local signature (Usage: lsign <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--lsign-key', *args.tuple)
            else:
                self.do_help('lsign')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_sign(self, args):
        """Sign a key with an exportable signature (Usage: sign <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--sign-key', *args.tuple)
            else:
                self.do_help('sign')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_del(self, args):
        """Delete a key from the keyring (Usage: del <keyspec>)"""
        args = parseargs(args)
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
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_search(self, args):
        """Search for keys on a keyserver (Usage: search <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--search-keys', *args.tuple)
            else:
                self.do_help('search')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_recv(self, args):
        """Fetch keys from a keyserver (Usage: recv <keyids>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--recv-keys', *args.tuple)
            else:
                self.do_help('recv')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_send(self, args):
        """Send keys to a keyserver (Usage: send <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--send-keys', *args.tuple)
            else:
                self.do_help('send')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_refresh(self, args):
        """Refresh keys from a keyserver (Usage: refresh [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            self.gnupg('--refresh-keys', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_fetch(self, args):
        """Fetch keys from a URL (Usage: fetch <url>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--fetch-keys', *args.tuple)
            else:
                self.do_help('fetch')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_dump(self, args):
        """Print the packet sequence of keys (Usage: dump [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            command = '--export'
            if args.secret:
                command = '--export-secret-keys'
            tuple = args.options + args.args + ('|', GNUPGEXE, '--list-packets') + args.pipe
            self.gnupg(command, *tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_fdump(self, args):
        """Print the packet sequence of keys in a file (Usage: fdump <filename>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.gnupg('--list-packets', *args.tuple)
            elif not self.looping:
                self.gnupg('--list-packets', '-')
            else:
                self.do_help('fdump')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)

    def do_shell(self, args):
        """Execute a shell command or start an interactive shell (Usage: ! [<command>])"""
        args = splitargs(args)
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
            elif cmd == 'man':
                self.shell_man(*args[1:])
            else:
                self.shelldefault(*args)
        else:
            self.system(os.environ.get('SHELL'))

    # Shell commands

    def getdir(self, dir):
        rc, stdout = self.popen('cd %s; pwd' % dir, stdout=subprocess.PIPE)
        if rc == 0:
            if sys.version_info[0] >= 3:
                stdout = decode(stdout)
            for line in stdout.strip().split('\n'):
                return line

    def shelldefault(self, *args):
        self.system(*args)

    def shell_ls(self, *args):
        self.system('ls', '-F', *args)

    def shell_ll(self, *args):
        self.system('ls', '-lF', *args)

    def shell_chdir(self, *args):
        if args:
            dir = self.getdir(args[0])
        else:
            dir = os.path.expanduser('~')
        if dir:
            try:
                os.chdir(dir)
            except OSError, e:
                self.stderr.write('%s\n' % (e,))

    def shell_umask(self, *args):
        if args:
            if self.system('umask', *args) == 0:
                try:
                    mask = int(args[0], 8)
                except ValueError, e:
                    self.stderr.write('%s\n' % (e,))
                else:
                    if mask < 512:
                        try:
                            os.umask(mask)
                        except OSError, e:
                            self.stderr.write('%s\n' % (e,))
        else:
            self.system('umask')

    def shell_man(self, *args):
        if args:
            if self.system('man', *args, stderr=subprocess.PIPE) == 1:
                args = ' '.join(args)
                self.stderr.write('No manual entry for %s\n' % args)
        else:
            self.stderr.write('What manual page do you want?\n')

    # Completions

    def completebase(self, word, default):
        """Complete after pipes and input/output redirects."""
        if word.pipepos:
            if not word.isfilename:
                return self.completecommand(word.text)
            return self.completefilename(word.text)
        if word.filepos:
            return self.completefilename(word.text)
        return default(word.text)

    def completeoption(self, text, options):
        """Complete from a list of options."""
        return [x for x in options if x.startswith(text)]

    def complete_genkey(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + EXPERT)
        return self.completebase(word, self.completedefault)

    def complete_genrevoke(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + OUTPUT)
        if word.follows('--output'):
            return self.completefilename(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_import(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + INPUT + CLEAN + MINIMAL)
        return self.completebase(word, self.completefilename)

    def complete_export(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + OUTPUT + SECRET + CLEAN + MINIMAL)
        if word.follows('--output'):
            return self.completefilename(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_list(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST + SECRET)
        return self.completebase(word, self.completekeyspec)

    def complete_listsig(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST)
        return self.completebase(word, self.completekeyspec)

    def complete_checksig(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST)
        return self.completebase(word, self.completekeyspec)

    def complete_edit(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN + EXPERT)
        if word.follows('--local-user'):
            return self.completekeyspec(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_lsign(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN)
        if word.follows('--local-user'):
            return self.completekeyspec(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_sign(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN)
        if word.follows('--local-user'):
            return self.completekeyspec(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_del(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + DELETE + SECRET)
        return self.completebase(word, self.completekeyspec)

    def complete_search(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + INPUT + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_recv(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + INPUT + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_send(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_refresh(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyspec)

    def complete_fetch(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + INPUT + CLEAN)
        return self.completebase(word, self.completedefault)

    def complete_dump(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SECRET + CLEAN + MINIMAL)
        return self.completebase(word, self.completekeyspec)

    def complete_fdump(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL)
        return self.completebase(word, self.completefilename)

    def complete_shell(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL)
        if word.commandpos:
            if not word.isfilename:
                return self.completecommand(word.text)
        return self.completebase(word, self.completefilename)

    # Help

    def do_help(self, topic=''):
        """Interactive help (Usage: help [<topic>])"""
        if topic:
            try:
                helpfunc = getattr(self, 'help_' + topic)
            except AttributeError:
                try:
                    dofunc = getattr(self, 'do_' + topic)
                except AttributeError:
                    pass
                else:
                    doc = dofunc.__doc__
                    cmd = dofunc.__name__[3:]
                    if doc:
                        rparen = doc.rfind(')')
                        lparen = doc.rfind('(', 0, rparen)
                        help = doc[:lparen].strip()
                        usage = doc[lparen+1:rparen].strip()

                        if topic == '?':
                            usage = usage.replace(cmd, '?', 1)
                        if topic == '.':
                            usage = usage.replace('!', '.', 1)

                        options = []
                        compfunc = getattr(self, 'complete_' + topic, None)
                        if compfunc is not None:
                            options = compfunc('-', '-', 0, 1)

                        self.stdout.write("%s\n" % usage)
                        if options:
                            options = ' '.join(sorted(options))
                            self.stdout.write("Options: %s\n" % options)
                        self.stdout.write("\n%s\n\n" % help)
                        return
                self.stderr.write('%s\n' % (self.nohelp % (topic,)))
            else:
                try:
                    helpfunc(topic)
                except TypeError:
                    helpfunc()
        else:
            self.help()


def main(args=None):
    quote_char = '\\'
    verbose = False
    help = False

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
            help = True

    shell = GPGKeys(quote_char=quote_char, verbose=verbose)

    if help:
        shell.help()
        print "Type '%s' to start the interactive shell.\n" % sys.argv[0]
        return 0

    return shell.run(args)


if __name__ == '__main__':
    sys.exit(main())

