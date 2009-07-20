import os
import sys
import cmd
import readline
import tl.cmd
import tl.readline


class MyCmd(tl.cmd.Cmd):

    # Set some readline options, decorate

    def do_foo(self, *args):
        "Do Foo"

    def do_bar(self, *args):
        "Do Bar"

    def do_baz(self, *args):
        "Do Baz"

    def preloop(self):
        tl.cmd.Cmd.preloop(self)
        #readline.parse_and_bind('set mark-directories on')
        #readline.parse_and_bind('set mark-symlinked-directories on')
        readline.set_completer_delims('\t\n`\'"!^/&?*<>|[]{}')
        #readline.set_completer_delims('')
        self.set_filecompleter()

    def completenames(self, text, *ignored):
        names = cmd.Cmd.completenames(self, text, *ignored)
        if len(names) == 1:
            # Switch to options completer or filename completer here
            name = names[0].strip()
        return names

    def set_filecompleter(self):
        completions = tl.readline.filename_completions(os.getcwd())
        readline.set_completer(tl.readline.completion_generator(completions))


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    c = MyCmd()
    if args:
        c.onecmd(' '.join(args))
    else:
        c.cmdloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())

