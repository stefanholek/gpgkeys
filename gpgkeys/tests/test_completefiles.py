import os
import unittest

from os.path import dirname

from gpgkeys.gpgkeys import GPGKeys


class CharIsQuotedTests(unittest.TestCase):

    def setUp(self):
        self.cmd = GPGKeys()
        self.cmd.preloop()
        self.cmd.file_completion.do_log = False
        self.is_quoted = self.cmd.file_completion.char_is_quoted

    def test_backslash_quoted_double_quote(self):
        self.assertEqual(self.is_quoted('\\"', 1), True)
        self.assertEqual(self.is_quoted('\\"', 0), True)
        self.assertEqual(self.is_quoted('\\ \\"', 3), True)
        self.assertEqual(self.is_quoted('\\ \\"', 2), True)
        self.assertEqual(self.is_quoted('\\ \\"', 1), True)
        self.assertEqual(self.is_quoted('\\ \\"', 0), True)

    def test_backslash_quoted_single_quote(self):
        self.assertEqual(self.is_quoted("\\'", 1), True)
        self.assertEqual(self.is_quoted("\\'", 0), True)

    def test_quoted_by_other_quote_character(self):
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 0), False)
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 5), True)
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 9), True)
        self.assertEqual(self.is_quoted("""'foo "bar"'""", 10), False)

    def test_quoted_by_quoted_other_quote_character(self):
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 0), True)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 1), True)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 5), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 6), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 10), False)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 11), True)
        self.assertEqual(self.is_quoted("""\\'foo "bar"\\'""", 12), True)

    def BORKEN_test_backslash_quoted_double_quote_preceeded_by_1_backslash(self):
        self.assertEqual(self.is_quoted('\\\\"', 2), False)
        self.assertEqual(self.is_quoted('\\\\"', 1), True)
        self.assertEqual(self.is_quoted('\\\\"', 0), True)

    def BORKEN_test_backslash_quoted_double_quote_preceeded_by_2_backslashes(self):
        self.assertEqual(self.is_quoted('\\\\\\"', 3), True)
        self.assertEqual(self.is_quoted('\\\\\\"', 2), True)
        self.assertEqual(self.is_quoted('\\\\\\"', 1), False)
        self.assertEqual(self.is_quoted('\\\\\\"', 0), True)

    def BORKEN_test_backslash_quoted_double_quote_preceeded_by_3_backslashes(self):
        self.assertEqual(self.is_quoted('\\\\\\\\"', 4), False)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 3), True)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 2), True)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 1), True)
        self.assertEqual(self.is_quoted('\\\\\\\\"', 0), True)

    def test_normaldir(self):
        self.assertEqual(self.is_quoted('normaldir/\\"', 11), True)
        self.assertEqual(self.is_quoted('normaldir/\\"', 10), True)
        self.assertEqual(self.is_quoted('normaldir/\\"', 9), False)

    def test_normaldir_hello(self):
        self.assertEqual(self.is_quoted('normaldir/\\"Hello\\ ', 18), True)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello ', 17), False)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello ', 11), True)
        self.assertEqual(self.is_quoted('normaldir/\\"Hello ', 10), True)

    def test_normaldir_hello_quoted(self):
        self.assertEqual(self.is_quoted('"normaldir/\\"Hello ', 18), True)
        self.assertEqual(self.is_quoted('"normaldir/\\"Hello ', 12), True)
        self.assertEqual(self.is_quoted('"normaldir/\\"Hello ', 11), True)


class CompleterTests(unittest.TestCase):

    def setUp(self):
        self.cmd = GPGKeys()
        self.cmd.preloop()
        self.cmd.file_completion.do_log = False
        os.chdir(dirname(__file__))

    def test_simple(self):
        self.assertEqual(self.cmd.completefiles('test_esc', 'fdump test_esc', 6, 13),
                         ['test_escape.py', 'test_escape.pyc'])

