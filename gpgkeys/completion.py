import readline # [sic]
import _readline as readline

import sys
import cmd as _cmd

_MAXMATCHES = 100000 # Just in case


def print_exc(func):
    """Decorator printing exceptions to stderr.

    Useful while debugging completers.
    """
    def wrapped_func(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            import traceback; traceback.print_exc()
            raise

    wrapped_func.__name__ = func.__name__
    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    return wrapped_func


class Completer(object):
    """Interface to the readline completer."""

    # For filename_quoting_function
    SINGLE_MATCH = 1
    MULT_MATCH = 2

    @apply
    def word_break_characters():
        def get(self):
            return readline.get_completer_delims()
        def set(self, string):
            readline.set_completer_delims(string)
        return property(get, set)

    @apply
    def special_prefixes():
        def get(self):
            return readline.get_special_prefixes()
        def set(self, string):
            readline.set_special_prefixes(string)
        return property(get, set)

    @apply
    def quote_characters():
        def get(self):
            return readline.get_completer_quote_characters()
        def set(self, string):
            readline.set_completer_quote_characters(string)
        return property(get, set)

    @apply
    def filename_quote_characters():
        def get(self):
            return readline.get_filename_quote_characters()
        def set(self, string):
            readline.set_filename_quote_characters(string)
        return property(get, set)

    @apply
    def tilde_expansion():
        def get(self):
            return readline.get_complete_with_tilde_expansion()
        def set(self, value):
            readline.set_complete_with_tilde_expansion(value)
        return property(get, set)

    @apply
    def match_hidden_files():
        def get(self):
            return readline.get_match_hidden_files()
        def set(self, value):
            readline.set_match_hidden_files(value)
        return property(get, set)

    @apply
    def query_items():
        def get(self):
            return readline.get_completion_query_items()
        def set(self, value):
            readline.set_completion_query_items(value)
        return property(get, set)

    @apply
    def completer():
        def get(self):
            return readline.get_completer()
        def set(self, function):
            readline.set_completer(function)
        return property(get, set)

    @apply
    def startup_hook():
        def get(self):
            return readline.get_startup_hook()
        def set(self, function):
            readline.set_startup_hook(function)
        return property(get, set)

    @apply
    def pre_input_hook():
        def get(self):
            return readline.get_pre_input_hook()
        def set(self, function):
            readline.set_pre_input_hook(function)
        return property(get, set)

    @apply
    def word_break_hook():
        def get(self):
            return readline.get_completion_word_break_hook()
        def set(self, function):
            readline.set_completion_word_break_hook(function)
        return property(get, set)

    @apply
    def display_matches_hook():
        def get(self):
            return readline.get_completion_display_matches_hook()
        def set(self, function):
            readline.set_completion_display_matches_hook(function)
        return property(get, set)

    @apply
    def directory_completion_hook():
        def get(self):
            return readline.get_directory_completion_hook()
        def set(self, function):
            readline.set_directory_completion_hook(function)
        return property(get, set)

    @apply
    def char_is_quoted_function():
        def get(self):
            return readline.get_char_is_quoted_function()
        def set(self, function):
            readline.set_char_is_quoted_function(function)
        return property(get, set)

    @apply
    def filename_quoting_function():
        def get(self):
            return readline.get_filename_quoting_function()
        def set(self, function):
            readline.set_filename_quoting_function(function)
        return property(get, set)

    @apply
    def filename_dequoting_function():
        def get(self):
            return readline.get_filename_dequoting_function()
        def set(self, function):
            readline.set_filename_dequoting_function(function)
        return property(get, set)

    # Extra API

    @property
    def preferred_quote_character(self):
        if self.quote_characters:
            return self.quote_characters[0]
        return ''

    # Configuration

    def read_init_file(self, filename):
        return readline.read_init_file(filename)

    def parse_and_bind(self, line):
        return readline.parse_and_bind(line)

    # Debugging

    @print_exc
    def dump_vars(self):
        sys.stdout.write("""
word_break_characters:          %r
special_prefixes:               %r
quote_characters:               %r
filename_quote_characters:      %r
tilde_expansion:                %s
match_hidden_files:             %s
query_items:                    %d
preferred_quote_character:      %r
completer:                      %r
startup_hook:                   %r
pre_input_hook:                 %r
word_break_hook:                %r
display_matches_hook:           %r
directory_completion_hook:      %r
char_is_quoted_function:        %r
filename_quoting_function:      %r
filename_dequoting_function:    %r
""" % (
completer.word_break_characters,
completer.special_prefixes,
completer.quote_characters,
completer.filename_quote_characters,
completer.tilde_expansion,
completer.match_hidden_files,
completer.query_items,
completer.preferred_quote_character,
completer.completer,
completer.startup_hook,
completer.pre_input_hook,
completer.word_break_hook,
completer.display_matches_hook,
completer.directory_completion_hook,
completer.char_is_quoted_function,
completer.filename_quoting_function,
completer.filename_dequoting_function,
))

completer = Completer()


class Completion(object):
    """Interface to the current readline completion."""

    @property
    def line_buffer(self):
        return readline.get_line_buffer()

    @property
    def begidx(self):
        return readline.get_begidx()

    @property
    def endidx(self):
        return readline.get_endidx()

    @property
    def completion_type(self):
        return readline.get_completion_type()

    @property
    def invoking_key(self):
        return readline.get_completion_invoking_key()

    @property
    def found_quote(self):
        return readline.get_completion_found_quote()

    @property
    def quote_character(self):
        return readline.get_completion_quote_character()

    @apply
    def append_character():
        def get(self):
            return readline.get_completion_append_character()
        def set(self, string):
            readline.set_completion_append_character(string)
        return property(get, set)

    @apply
    def suppress_append():
        def get(self):
            return readline.get_completion_suppress_append()
        def set(self, value):
            readline.set_completion_suppress_append(value)
        return property(get, set)

    @apply
    def suppress_quote():
        def get(self):
            return readline.get_completion_suppress_quote()
        def set(self, value):
            readline.set_completion_suppress_quote(value)
        return property(get, set)

    @apply
    def attempted_completion_over():
        def get(self):
            return readline.get_attempted_completion_over()
        def set(self, value):
            readline.set_attempted_completion_over(value)
        return property(get, set)

    @apply
    def filename_completion_desired():
        def get(self):
            return readline.get_filename_completion_desired()
        def set(self, value):
            readline.set_filename_completion_desired(value)
        return property(get, set)

    @apply
    def filename_quoting_desired():
        def get(self):
            return readline.get_filename_quoting_desired()
        def set(self, value):
            readline.set_filename_quoting_desired(value)
        return property(get, set)

    @apply
    def sort_matches():
        def get(self):
            return readline.get_sort_completion_matches()
        def set(self, value):
            readline.set_sort_completion_matches(value)
        return property(get, set)

    @apply
    def ignore_duplicates():
        def get(self):
            return readline.get_ignore_completion_duplicates()
        def set(self, value):
            readline.set_ignore_completion_duplicates(value)
        return property(get, set)

    @apply
    def mark_symlink_dirs():
        def get(self):
            return readline.get_completion_mark_symlink_dirs()
        def set(self, value):
            readline.set_completion_mark_symlink_dirs(value)
        return property(get, set)

    @apply
    def inhibit_completion():
        def get(self):
            return readline.get_inhibit_completion()
        def set(self, value):
            readline.set_inhibit_completion(value)
        return property(get, set)

    # Line buffer manipulation

    def insert_text(self, text):
        return readline.insert_text(text)

    def stuff_char(self, char):
        return readline.stuff_char(char)

    def redisplay(self):
        return readline.redisplay()

    # Stock completions

    def complete_filename(self, text):
        new = []
        for i in range(_MAXMATCHES):
            n = readline.filename_completion_function(text, i)
            if n is not None:
                new.append(n)
            else:
                break
        return new

    def complete_username(self, text):
        new = []
        for i in range(_MAXMATCHES):
            n = readline.username_completion_function(text, i)
            if n is not None:
                new.append(n)
            else:
                break
        return new

    def expand_tilde(self, text):
        return readline.tilde_expand(text)

    # Debugging

    @print_exc
    def dump_vars(self):
        sys.stdout.write("""
line_buffer:                    %r
begidx:                         %s
endidx:                         %s
completion_type:                %s (%r)
append_character:               %r
suppress_append:                %s
found_quote:                    %s
quote_character:                %r
suppress_quote:                 %s
attempted_completion_over:      %s
filename_completion_desired:    %s
filename_quoting_desired:       %s
invoking_key:                   %s (%r)
sort_matches:                   %s
ignore_duplicates:              %s
mark_symlink_dirs:              %s
inhibit_completion:             %s
""" % (
completion.line_buffer,
completion.begidx,
completion.endidx,
completion.completion_type, chr(completion.completion_type),
completion.append_character,
completion.suppress_append,
completion.found_quote,
completion.quote_character,
completion.suppress_quote,
completion.attempted_completion_over,
completion.filename_completion_desired,
completion.filename_quoting_desired,
completion.invoking_key, chr(completion.invoking_key),
completion.sort_matches,
completion.ignore_duplicates,
completion.mark_symlink_dirs,
completion.inhibit_completion,
))

completion = Completion()


class cmd:
    # Override some methods so they use completion's version of readline.

    class Cmd(_cmd.Cmd):
        """A simple framework for writing line-oriented command interpreters.

        These are often useful for test harnesses, administrative tools, and
        prototypes that will later be wrapped in a more sophisticated interface.

        A Cmd instance or subclass instance is a line-oriented interpreter
        framework.  There is no good reason to instantiate Cmd itself; rather,
        it's useful as a superclass of an interpreter class you define yourself
        in order to inherit Cmd's methods and encapsulate action methods.
        """

        def cmdloop(self, intro=None):
            """Repeatedly issue a prompt, accept input, parse an initial prefix
            off the received input, and dispatch to action methods, passing them
            the remainder of the line as argument.
            """
            self.preloop()
            if self.use_rawinput and self.completekey:
                self.old_completer = completer.completer
                completer.completer = self.complete
                completer.parse_and_bind(self.completekey+": complete")
            try:
                if intro is not None:
                    self.intro = intro
                if self.intro:
                    self.stdout.write(str(self.intro)+"\n")
                stop = None
                while not stop:
                    if self.cmdqueue:
                        line = self.cmdqueue.pop(0)
                    else:
                        if self.use_rawinput:
                            try:
                                line = raw_input(self.prompt)
                            except EOFError:
                                line = 'EOF'
                        else:
                            self.stdout.write(self.prompt)
                            self.stdout.flush()
                            line = self.stdin.readline()
                            if not len(line):
                                line = 'EOF'
                            else:
                                line = line[:-1] # chop \n
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)
                self.postloop()
            finally:
                if self.use_rawinput and self.completekey:
                    completer.completer = self.old_completer

        def complete(self, text, state):
            """Return the next possible completion for 'text'.

            If a command has not been entered, then complete against command list.
            Otherwise try to call complete_<command> to get list of completions.
            """
            if state == 0:
                origline = completion.line_buffer
                line = origline.lstrip()
                stripped = len(origline) - len(line)
                begidx = completion.begidx - stripped
                endidx = completion.endidx - stripped
                if begidx>0:
                    cmd, args, foo = self.parseline(line)
                    if cmd == '':
                        compfunc = self.completedefault
                    else:
                        try:
                            compfunc = getattr(self, 'complete_' + cmd)
                        except AttributeError:
                            compfunc = self.completedefault
                else:
                    compfunc = self.completenames
                self.completion_matches = compfunc(text, line, begidx, endidx)
            try:
                return self.completion_matches[state]
            except IndexError:
                return None

