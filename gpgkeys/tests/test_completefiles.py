import os
import unittest

from os.path import dirname

from gpgkeys.gpgkeys import GPGKeys
from gpgkeys.testing import TreeSetup
from gpgkeys.filename import FilenameCompletion

from rl import completer
from rl import completion
from rl import readline


class CompleterTests(TreeSetup):

    def setUp(self):
        TreeSetup.setUp(self)
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        self.completefilenames = FilenameCompletion(quote_char='"')
        completer.completer = self.cmd.complete
        os.chdir('normaldir')

    def complete(self, text):
        completion.line_buffer = text
        readline.complete_internal('\t')
        return completion.line_buffer

    def test_simple(self):
        self.assertEqual(self.complete('fdump Simple'),
                         'fdump Simple.txt ')

    def test_hello(self):
        self.assertEqual(self.complete('fdump Hell'),
                         'fdump "Hello World.txt" ')

    def test_hello_quote(self):
        self.assertEqual(self.complete('fdump "Hello '),
                         'fdump "Hello World.txt" ')

    def test_hello_single_quote(self):
        self.assertEqual(self.complete("fdump 'Hello "),
                         "fdump 'Hello World.txt' ")

    def test_lee(self):
        self.assertEqual(self.complete('fdump Lee'),
                         'fdump "Lee \\"Scratch\\" Perry.txt" ')

    def test_lee_quote(self):
        self.assertEqual(self.complete('''fdump "Lee \\"'''),
                         'fdump "Lee \\"Scratch\\" Perry.txt" ')

    def test_lee_single_quote(self):
        self.assertEqual(self.complete('''fdump 'Lee "'''),
                         '''fdump 'Lee "Scratch" Perry.txt' ''')


class CharIsQuotedTests(unittest.TestCase):

    def setUp(self):
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        self.is_quoted = self.cmd.completefilenames.char_is_quoted

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

