# gpgkeys
#

from __future__ import with_statement

import locale
locale.setlocale(locale.LC_ALL, '')

import pkg_resources
__version__ = pkg_resources.get_distribution('gpgkeys').version

import os
import sys
import getopt
import subprocess
import kmd
import term

from parser import splitargs
from parser import parseargs
from parser import parseword

from utils import decode
from utils import surrogateescape
from utils import ignoresignals
from utils import savettystate
from utils import conditional

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
    history_max_entries = 200

    intro = 'gpgkeys %s (type help for help)\n' % __version__
    nohelp = "gpgkeys: no help on '%s'"
    doc_header = 'Available commands (type help <topic>):'
    alias_header = 'Shortcut commands (type help <topic>):'

    def __init__(self, completekey='TAB', stdin=None, stdout=None, stderr=None,
                 quote_char='\\', verbose=False):
        super(GPGKeys, self).__init__(completekey, stdin, stdout, stderr)
        self.quote_char = quote_char
        self.verbose = verbose
        self.is_looping = False
        self.rc = 0
        self.aliases['e'] = 'edit'
        self.aliases['ls'] = 'list'
        self.aliases['ll'] = 'listsig'
        os.umask(UMASK)

    def preloop(self):
        super(GPGKeys, self).preloop()
        self.is_looping = True
        # Setup completions
        self.completefilename = FilenameCompletion(self.quote_char)
        self.completecommand = CommandCompletion()
        self.completekeyid = KeyCompletion()
        self.completekeyserver = KeyserverCompletion()

    def postloop(self):
        self.is_looping = False
        super(GPGKeys, self).postloop()

    def input(self, prompt):
        # Allow surrogates in input
        # See http://bugs.python.org/issue13342
        with surrogateescape():
            return super(GPGKeys, self).input(prompt)

    def onecmd(self, line):
        self.rc = 0
        return super(GPGKeys, self).onecmd(line)

    def run(self, args=None):
        rc = super(GPGKeys, self).run(args)
        if rc == 1: # KeyboardInterrupt
            self.rc = rc
        return self.rc

    # Execute subprocesses

    def has_pager(self, args):
        for x in ('less', 'more', 'most', 'view', 'man'):
            if x in args:
                return True

    def popen(self, *args, **kw):
        command = ' '.join(args)
        stdout = kw.get('stdout', None)
        stderr = kw.get('stderr', None)
        with savettystate():
            try:
                process = subprocess.Popen(command, shell=True, stdout=stdout, stderr=stderr)
                stdoutdata, stderrdata = process.communicate()
                return process.returncode, stdoutdata
            except KeyboardInterrupt:
                return 1, None

    def getoutput(self, *args, **kw):
        rc, output = self.popen(*args, **dict(kw, stdout=subprocess.PIPE))
        if rc == 0 and output is not None:
            if sys.version_info[0] >= 3:
                output = decode(output)
            if output.strip():
                # Return first line only
                return output.split('\n', 1)[0]
        return ''

    def system(self, *args, **kw):
        with conditional(self.has_pager(args), ignoresignals()):
            return self.popen(*args, **kw)[0]

    def gnupg(self, *args, **kw):
        if self.verbose:
            self.stderr.write('gpgkeys: %s %s\n' % (GNUPGEXE, ' '.join(args)))
        return self.system(GNUPGEXE, *args, **kw)

    # Commands

    def emptyline(self):
        """Empty line"""
        pass

    def default(self, args):
        """Unknown command"""
        args = splitargs(args)
        self.stderr.write("gpgkeys: unknown command '%s'\n" % args[0])
        self.rc = 1

    def do_EOF(self, args):
        """End the session (Usage: ^D)"""
        if self.is_looping:
            self.stdout.write('\n')
        return self.do_quit(args)

    def do_quit(self, args):
        """End the session (Usage: quit)"""
        return True # Break the cmd loop

    def do_clear(self, args):
        """Clear the screen (Usage: clear)"""
        self.system('clear')

    def do_version(self, args):
        """Print the GnuPG version (Usage: version)"""
        self.rc = self.gnupg('--version')

    def do_genkey(self, args):
        """Generate a new key pair and certificate (Usage: genkey)"""
        args = parseargs(args)
        if args.ok:
            self.rc = self.gnupg('--gen-key', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_genrevoke(self, args):
        """Generate a revocation certificate for a key (Usage: genrevoke <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--gen-revoke', *args.tuple)
            else:
                self.do_help('genrevoke')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_import(self, args):
        """Import keys from a file (Usage: import <filename>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--import', *args.tuple)
            elif args.pipe and args.pipe[0] == '<':
                self.rc = self.gnupg('--import', *args.tuple)
            elif not self.is_looping:
                args.args = ('-',)
                self.rc = self.gnupg('--import', *args.tuple)
            else:
                self.do_help('import')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_export(self, args):
        """Export keys to stdout or to a file (Usage: export [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            command = '--export'
            if args.secret:
                command = '--export-secret-keys'
            self.rc = self.gnupg(command, *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_list(self, args):
        """List keys (Usage: list [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            command = '--list-keys'
            if args.secret:
                command = '--list-secret-keys'
            self.rc = self.gnupg(command, *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_listsig(self, args):
        """List keys with signatures (Usage: listsig [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            self.rc = self.gnupg('--list-sigs', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_checksig(self, args):
        """List keys with signatures and also verify the signatures (Usage: checksig [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            self.rc = self.gnupg('--check-sigs', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_edit(self, args):
        """Enter the key edit menu (Usage: edit <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--edit-key', *args.tuple)
                # When the edit menu is exited with ^D the cursor
                # is left in column 6; fix that.
                if self.rc == 0:
                    if term.getyx()[1] > 1:
                        self.stdout.write('\n')
            else:
                self.do_help('edit')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_lsign(self, args):
        """Sign a key with a local signature (Usage: lsign <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--lsign-key', *args.tuple)
            else:
                self.do_help('lsign')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_sign(self, args):
        """Sign a key with an exportable signature (Usage: sign <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--sign-key', *args.tuple)
            else:
                self.do_help('sign')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

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
                self.rc = self.gnupg(command, *args.tuple)
            else:
                self.do_help('del')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_search(self, args):
        """Search for keys on a keyserver (Usage: search <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--search-keys', *args.tuple)
            else:
                self.do_help('search')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_recv(self, args):
        """Fetch keys from a keyserver (Usage: recv <keyids>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--recv-keys', *args.tuple)
            else:
                self.do_help('recv')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_send(self, args):
        """Send keys to a keyserver (Usage: send <keyspec>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--send-keys', *args.tuple)
            else:
                self.do_help('send')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_refresh(self, args):
        """Refresh keys from a keyserver (Usage: refresh [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            self.rc = self.gnupg('--refresh-keys', *args.tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_fetch(self, args):
        """Fetch keys from a URL (Usage: fetch <url>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--fetch-keys', *args.tuple)
            else:
                self.do_help('fetch')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_dump(self, args):
        """Print the packet sequence of keys (Usage: dump [<keyspec>])"""
        args = parseargs(args)
        if args.ok:
            command = '--export'
            if args.secret:
                command = '--export-secret-keys'
            tuple = args.options + args.args + ('|', GNUPGEXE, '--list-packets') + args.pipe
            self.rc = self.gnupg(command, *tuple)
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

    def do_fdump(self, args):
        """Print the packet sequence of keys in a file (Usage: fdump <filename>)"""
        args = parseargs(args)
        if args.ok:
            if args.args:
                self.rc = self.gnupg('--list-packets', *args.tuple)
            elif args.pipe and args.pipe[0] == '<':
                self.rc = self.gnupg('--list-packets', *args.tuple)
            elif not self.is_looping:
                args.args = ('-',)
                self.rc = self.gnupg('--list-packets', *args.tuple)
            else:
                self.do_help('fdump')
        else:
            self.stderr.write('gpgkeys: %s\n' % args.error)
            self.rc = 1

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
                self.system(*args)
        else:
            self.system(os.environ.get('SHELL'))

    # Shell commands

    def shell_ls(self, *args):
        self.system('ls', '-F', *args)

    def shell_ll(self, *args):
        self.system('ls', '-lF', *args)

    def shell_chdir(self, *args):
        if args:
            dir = self.getoutput('cd %s; pwd' % args[0])
        else:
            dir = os.path.expanduser('~')
        if dir:
            try:
                os.chdir(dir)
            except OSError, e:
                self.stderr.write('%s\n' % (e,))
                self.rc = 1

    def shell_umask(self, *args):
        if args:
            if self.system('umask', *args) == 0:
                try:
                    mask = int(args[0], 8)
                except ValueError, e:
                    self.stderr.write('%s\n' % (e,))
                    self.rc = 1
                else:
                    if mask < 512:
                        try:
                            os.umask(mask)
                        except OSError, e:
                            self.stderr.write('%s\n' % (e,))
                            self.rc = 1
        else:
            self.system('umask')

    def shell_man(self, *args):
        if args:
            if self.system('man', *args, **dict(stderr=subprocess.PIPE)) == 1:
                self.stderr.write('No manual entry for %s\n' % ' '.join(args))
                self.rc = 1
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
        return self.completebase(word, self.completekeyid)

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
        return self.completebase(word, self.completekeyid)

    def complete_list(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST + SECRET)
        return self.completebase(word, self.completekeyid)

    def complete_listsig(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST)
        return self.completebase(word, self.completekeyid)

    def complete_checksig(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + LIST)
        return self.completebase(word, self.completekeyid)

    def complete_edit(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN + EXPERT)
        if word.follows('--local-user'):
            return self.completekeyid(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_lsign(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN)
        if word.follows('--local-user'):
            return self.completekeyid(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_sign(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + KEY + SIGN)
        if word.follows('--local-user'):
            return self.completekeyid(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_del(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + DELETE + SECRET)
        return self.completebase(word, self.completekeyid)

    def complete_search(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + INPUT + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_recv(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + INPUT + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_send(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_refresh(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SERVER + CLEAN)
        if word.follows('--keyserver'):
            return self.completekeyserver(word.text)
        return self.completebase(word, self.completekeyid)

    def complete_fetch(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + INPUT + CLEAN)
        return self.completebase(word, self.completedefault)

    def complete_dump(self, text, line, begidx, endidx):
        word = parseword(line, begidx, endidx)
        if word.isoption:
            return self.completeoption(word.text, GLOBAL + SECRET + CLEAN + MINIMAL)
        return self.completebase(word, self.completekeyid)

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
                        if -1 < lparen < rparen:
                            help = doc[:lparen].strip()
                            usage = doc[lparen+1:rparen].strip()
                        else:
                            help, usage = doc.strip(), ''

                        if topic == '?':
                            usage = usage.replace(cmd, '?', 1)
                        if topic == '.':
                            usage = usage.replace('!', '.', 1)

                        options = []
                        compfunc = getattr(self, 'complete_' + topic, None)
                        if compfunc is not None:
                            options = compfunc('-', '-', 0, 1)

                        aliases = [k for (k, v) in self.aliases.iteritems() if v == cmd]
                        if cmd in ('shell', 'help'):
                            aliases = [x for x in aliases if x != topic]
                        if topic == 'shell':
                            aliases = [x for x in aliases if x != '!']

                        if usage:
                            self.stdout.write("%s\n" % usage)
                        if options:
                            options = ' '.join(sorted(options))
                            self.stdout.write("Options: %s\n" % options)
                        if aliases:
                            aliases = ' '.join(sorted(aliases))
                            self.stdout.write("Aliases: %s\n" % aliases)
                        if usage or options or aliases:
                            self.stdout.write("\n")
                        self.stdout.write("%s\n\n" % help)
                        return
                self.stderr.write('%s\n' % (self.nohelp % (topic,)))
                self.rc = 1
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
    version = False

    if args is None:
        args = sys.argv[1:]

    try:
        options, args = getopt.getopt(args, 'hq:v', ('help', 'quote-char=', 'verbose', 'version'))
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
        elif name in ('--version',):
            version = True

    shell = GPGKeys(quote_char=quote_char, verbose=verbose)

    if help:
        shell.help()
        print "Type 'gpgkeys' to start the interactive shell.\n"
        return 0
    if version:
        print 'gpgkeys', __version__
        return 0

    return shell.run(args)


if __name__ == '__main__':
    sys.exit(main())

