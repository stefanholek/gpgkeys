# -*- coding: utf-8 -*-

import unittest

from rl import completer
from rl import completion
from rl import readline

from gpgkeys.gpgkeys import GPGKeys
from gpgkeys.testing import JailSetup
from gpgkeys.testing import reset

TAB = '\t'


class CompleterTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer(quote_char='"')
        completer.completer = self.cmd.complete
        self.mkfiles()

    def complete(self, text):
        completion.line_buffer = text
        readline.complete_internal(TAB)
        return completion.line_buffer

    def mkfiles(self):
        self.mkfile("Al'Hambra.txt")
        self.mkfile('Foo\\"Peng\\".txt')
        self.mkfile('Foo\\Bar.txt')
        self.mkfile('Foo\\Baz.txt')
        self.mkfile('Hello World.txt')
        self.mkfile('Lee "Scratch" Perry.txt')
        self.mkfile('Mädchen.txt')
        self.mkfile('Simple.txt')
        self.mkfile('Tilde.tx~')
        self.mkfile('~StartsWithTilde.txt')

    def test_simple(self):
        self.assertEqual(self.complete('fdump Simple'),
                                       'fdump Simple.txt ')

    def test_hello(self):
        self.assertEqual(self.complete('fdump Hell'),
                                       'fdump "Hello World.txt" ')

    def test_hello_double_quote(self):
        self.assertEqual(self.complete('fdump "Hello '),
                                       'fdump "Hello World.txt" ')

    def test_hello_single_quote(self):
        self.assertEqual(self.complete("fdump 'Hello "),
                                       "fdump 'Hello World.txt' ")

    def test_lee(self):
        self.assertEqual(self.complete('fdump Lee'),
                                       'fdump "Lee \\"Scratch\\" Perry.txt" ')

    def test_lee_double_quote(self):
        self.assertEqual(self.complete('fdump "Lee \\"'),
                                       'fdump "Lee \\"Scratch\\" Perry.txt" ')

    def test_lee_single_quote(self):
        self.assertEqual(self.complete('''fdump 'Lee "'''),
                                       '''fdump 'Lee "Scratch" Perry.txt' ''')

    def test_foobar(self):
        self.assertEqual(self.complete('fdump Foo'),
                                       'fdump Foo\\\\')

    def test_foobar_double_quote(self):
        self.assertEqual(self.complete('fdump "Foo'),
                                       'fdump "Foo\\\\')

    def test_foobar_single_quote(self):
        self.assertEqual(self.complete("fdump 'Foo"),
                                       "fdump 'Foo\\")

    def test_alhambra(self):
        self.assertEqual(self.complete('fdump Al'),
                                     '''fdump "Al'Hambra.txt" ''')

    def test_alhambra_double_quote(self):
        self.assertEqual(self.complete('fdump "Al'),
                                     '''fdump "Al'Hambra.txt" ''')

    def test_alhambra_single_quote(self):
        self.assertEqual(self.complete("fdump 'Al"),
                                       "fdump 'Al'\\''Hambra.txt' ")

    def test_foopeng(self):
        self.assertEqual(self.complete('fdump Foo\\\\\\"'),
                                       'fdump Foo\\\\\\"Peng\\\\\\".txt ')

    def test_foopeng_double_quote(self):
        self.assertEqual(self.complete('fdump "Foo\\\\\\"'),
                                       'fdump "Foo\\\\\\"Peng\\\\\\".txt" ')

    def test_foopeng_single_quote(self):
        self.assertEqual(self.complete('''fdump 'Foo\\"'''),
                                       '''fdump 'Foo\\"Peng\\".txt' ''')

    def test_tilde(self):
        self.assertEqual(self.complete('fdump Tilde'),
                                       'fdump Tilde.tx~ ')

    def test_starts_with_tilde(self):
        self.assertEqual(self.complete('fdump ~Starts'),
                                       'fdump ~StartsWithTilde.txt ')

    def test_returned_umlaut(self):
        self.assertEqual(self.complete('fdump M'),
                                       'fdump Mädchen.txt ')

    def test_typed_umlaut(self):
        self.assertEqual(self.complete('fdump Mä'),
                                       'fdump Mädchen.txt ')


class CharIsQuotedTests(unittest.TestCase):

    def setUp(self):
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer(quote_char='"')
        self.is_quoted = self.cmd.completefilename.char_is_quoted

    def test_backslash_quoted_double_quote(self):
        self.assertEqual(self.is_quoted('\\"', 1), True)
        self.assertEqual(self.is_quoted('\\"', 0), False)
        self.assertEqual(self.is_quoted('\\ \\"', 3), True)
        self.assertEqual(self.is_quoted('\\ \\"', 2), False)
        self.assertEqual(self.is_quoted('\\ \\"', 1), True)
        self.assertEqual(self.is_quoted('\\ \\"', 0), False)

    def test_backslash_quoted_single_quote(self):
        self.assertEqual(self.is_quoted("\\'", 1), True)
        self.assertEqual(self.is_quoted("\\'", 0), False)

    def test_quoted_by_other_quote_character(self):
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 0), False)
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 5), True)
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 9), True)
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 10), False)

    def test_quoted_by_quoted_other_quote_character(self):
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 0), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 1), True)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 5), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 6), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 10), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 11), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 12), True)

    def test_backslash_quoted_double_quote_preceeded_by_1_backslash(self):
        self.assertEqual(self.is_quoted('\\\\"', 2), False)
        self.assertEqual(self.is_quoted('\\\\"', 1), True)
        self.assertEqual(self.is_quoted('\\\\"', 0), False)

    def test_backslash_quoted_double_quote_preceeded_by_2_backslashes(self):
        self.assertEqual(self.is_quoted('\\\\\\"', 3), True)
        self.assertEqual(self.is_quoted('\\\\\\"', 2), False)
        self.assertEqual(self.is_quoted('\\\\\\"', 1), True)
        self.assertEqual(self.is_quoted('\\\\\\"', 0), False)

    def test_backslash_quoted_double_quote_preceeded_by_3_backslashes(self):
        self.assertEqual(self.is_quoted('\\\\\\\\"', 4), False)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 3), True)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 2), False)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 1), True)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 0), False)

    def test_normaldir(self):
        self.assertEqual(self.is_quoted('normaldir/\\"', 11), True)
        self.assertEqual(self.is_quoted('normaldir/\\"', 10), False)
        self.assertEqual(self.is_quoted('normaldir/\\"', 9), False)

    def test_normaldir_hello(self):
        self.assertEqual(self.is_quoted('normaldir/\\"Hello ', 17), False)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello ', 11), True)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello ', 10), False)

    def test_normaldir_hello_quoted(self):
        self.assertEqual(self.is_quoted('"normaldir/\\"Hello ', 18), True)
        self.assertEqual(self.is_quoted('"normaldir/\\"Hello ', 12), True)
        self.assertEqual(self.is_quoted('"normaldir/\\"Hello ', 11), True)

    def test_normaldir_hello_quoted_space(self):
        self.assertEqual(self.is_quoted('normaldir/\\"Hello\\ ', 18), True)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello\\ ', 17), False)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello\\ ', 11), True)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello\\ ', 10), False)


class DirectoryCompletionHookTests(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer(quote_char='\\')
        completer.completer = self.cmd.complete
        self.mkfiles()

    def complete(self, text):
        completion.line_buffer = text
        readline.complete_internal(TAB)
        return completion.line_buffer

    def mkfiles(self):
        self.mkdir('funny dir')
        self.mkfile('funny dir/foo.txt')
        self.mkfile('funny dir/foo.gif')

    def test_dir_completion(self):
        self.assertEqual(self.complete('fdump fun'),
                                       'fdump funny\\ dir/')

    def test_no_dir_completion_hook(self):
        # The current implementation works without a
        # directory_completion_hook.
        completer.directory_completion_hook = None
        self.assertEqual(self.complete('fdump funny\\ dir/f'),
                                       'fdump funny\\ dir/foo.')

    def test_dir_completion_hook(self):
        # Even if a hook is installed, it never receives a
        # quoted directory name.
        called = []
        def hook(text):
            called.append((text,))
            return text

        completer.directory_completion_hook = hook
        self.assertEqual(self.complete('fdump funny\\ dir/f'),
                                       'fdump funny\\ dir/foo.')
        self.assertEqual(called, [('funny dir/',)])


class InitQuoteCharactersTests(unittest.TestCase):

    def setUp(self):
        reset()
        self.cmd = GPGKeys()

    def test_double_quote(self):
        self.cmd.init_completer('"')
        self.assertEqual(completer.quote_characters, '"\'')

    def test_single_quote(self):
        self.cmd.init_completer("'")
        self.assertEqual(completer.quote_characters, '\'"')

    def test_backslash(self):
        self.cmd.init_completer('\\')
        self.assertEqual(completer.quote_characters, '"\'')

    def test_reconfigure(self):
        self.cmd.init_completer('"')
        self.assertEqual(completer.quote_characters, '"\'')
        self.cmd.init_completer("'")
        self.assertEqual(completer.quote_characters, '\'"')
        self.cmd.init_completer('"')
        self.assertEqual(completer.quote_characters, '"\'')
        self.cmd.init_completer("'")
        self.assertEqual(completer.quote_characters, '\'"')
        self.cmd.init_completer('\\')
        self.assertEqual(completer.quote_characters, '"\'')

    def test_invalid(self):
        self.assertRaises(ValueError, self.cmd.init_completer, 'A')

