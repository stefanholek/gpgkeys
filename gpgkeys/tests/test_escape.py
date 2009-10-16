import unittest

from gpgkeys.escape import char_is_quoted
from gpgkeys.escape import split


class CharIsQuotedTests(unittest.TestCase):

    TRUE_END = (
        '"',
        '"foo',
        'f"oo',
        'fo"o',
        'foo"',
        '\'',
        '\'foo',
        'f\'oo',
        'fo\'o',
        'foo\'',
        '\\',
        'foo\\',
        '"foo\\',
        '"foo\\"',
        '"foo\\"\\',
        '"foo"\\',
        '"foo\'',
        '"foo\\\'',
        '\'foo\\',
        '\'foo\\\'\\',
        '\'foo"',
        '\'foo\\"',
    )

    TRUE_LASTCHAR = (
        '" ',
        '"foo ',
        'f"oo ',
        'fo"o ',
        'foo" ',
        '\' ',
        '\'foo ',
        'f\'oo ',
        'fo\'o ',
        'foo\' ',
        '\\ ',
        'foo\\ ',
        '"foo\\ ',
        '"foo\\" ',
        '"foo\\"\\ ',
        '"foo"\\ ',
        '"foo\' ',
        '"foo\\\' ',
        '\'foo\\ ',
        '\'foo\\\'\\ ',
        '\'foo" ',
        '\'foo\\" ',
        '"foo \'bar\' ',
        '\'foo "bar" ',
        '"foo \'bar\'',
        '\'foo "bar"',
        '"foo \'bar\'\'',
        '\'foo "bar""',
    )

    FALSE_END = (
        'foo',
        'foo ',
        'fo\\o',
        'foo\\ ',
        'foo\\\\',
        '""',
        '"foo"',
        '"foo\'"',
        '\'\'',
        '\'foo\'',
        '\'foo\\\'',
        '\'foo"\'',
        '"foo \'bar\'"',
        '\'foo "bar"\'',
    )

    FALSE_LASTCHAR = (
        'foo ',
        'fo\\o ',
        'foo\\\\ ',
        '"" ',
        '"foo" ',
        '"foo\'" ',
        '\'\' ',
        '\'foo\' ',
        '\'foo\\\' ',
        '\'foo"\' ',
        # The closing quote character is NOT quoted
        '"foo \'bar\'"',
        '\'foo "bar"\'',
    )

    def test_true_end(self):
        for s in self.TRUE_END:
            self.assertEqual(char_is_quoted(s, len(s)), True, 'not True: %r' % s)

    def test_true_lastchar(self):
        for s in self.TRUE_LASTCHAR:
            self.assertEqual(char_is_quoted(s, len(s)-1), True, 'not True: %r' % s)

    def test_false_end(self):
        for s in self.FALSE_END:
            self.assertEqual(char_is_quoted(s, len(s)), False, 'not False: %r' % s)

    def test_false_lastchar(self):
        for s in self.FALSE_LASTCHAR:
            self.assertEqual(char_is_quoted(s, len(s)-1), False, 'not False: %r' % s)


class SplitTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(split('foo bar'), ('foo', 'bar'))

    def test_more_spaces(self):
        self.assertEqual(split('foo bar baz peng'), ('foo', 'bar', 'baz', 'peng'))

    def test_startswith_space(self):
        self.assertEqual(split(' foo'), ('foo',))

    def test_endswith_space(self):
        self.assertEqual(split('foo '), ('foo',))

    def test_double_space(self):
        self.assertEqual(split('foo  bar'), ('foo', 'bar'))

    def test_triple_space(self):
        self.assertEqual(split('foo   bar'), ('foo', 'bar'))

    def test_no_split_escaped(self):
        self.assertEqual(split('foo\\ bar'), ('foo\\ bar',))

    def test_no_split_escaped_more_spaces(self):
        self.assertEqual(split('foo bar\\ baz peng'), ('foo', 'bar\\ baz', 'peng'))

    def test_no_split_escaped_more_escapes(self):
        self.assertEqual(split('foo bar\\ baz fred\\ barney\\ wilma\\ \\ betty'),
                              ('foo', 'bar\\ baz', 'fred\\ barney\\ wilma\\ \\ betty'))


class DoubleQuoteSplitTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(split('"foo bar"'), ('"foo bar"',))

    def test_more_spaces(self):
        self.assertEqual(split('"foo bar baz peng"'), ('"foo bar baz peng"',))

    def test_startswith_space(self):
        self.assertEqual(split('" foo"'), ('" foo"',))

    def test_endswith_space(self):
        self.assertEqual(split('"foo "'), ('"foo "',))

    def test_double_space(self):
        self.assertEqual(split('"foo  bar"'), ('"foo  bar"',))

    def test_substring(self):
        self.assertEqual(split('foo bar "baz peng"'), ('foo', 'bar', '"baz peng"',))

    def test_substring_double_space(self):
        self.assertEqual(split('foo "bar baz"  peng'), ('foo', '"bar baz"', 'peng',))

    def test_substring_triple_space(self):
        self.assertEqual(split('foo   "bar baz" peng'), ('foo', '"bar baz"', 'peng',))

    def test_no_split_single_quote(self):
        self.assertEqual(split('foo "bar \'baz" peng'), ('foo', '"bar \'baz"', 'peng',))

    def test_startswith_escaped_single_quote(self):
        self.assertEqual(split('\\\'"foo bar "quux " baz peng'),
                              ("\\'", '"foo bar "', 'quux', '" baz peng'))

    def test_endswith_escaped_single_quote(self):
        self.assertEqual(split('"foo bar "quux " baz peng\\\''),
                              ('"foo bar "', 'quux', '" baz peng\\\'',))

    def test_no_split_escaped(self):
        self.assertEqual(split('foo "bar \\"quux\\" baz" peng'),
                              ('foo', '"bar \\"quux\\" baz"', 'peng',))

    def test_no_split_escaped_more_spaces(self):
        self.assertEqual(split('foo " bar \\"quux \\" baz" peng'),
                              ('foo', '" bar \\"quux \\" baz"', 'peng',))

    def test_startswith_escaped(self):
        self.assertEqual(split('\\"foo bar "quux " baz peng'),
                              ('\\"foo', 'bar', '"quux "', 'baz', 'peng',))

    def test_unquoted_spaces(self):
        self.assertEqual(split('\\"foo \\" bar " quux "'),
                              ('\\"foo', '\\"', 'bar', '" quux "',))

    def test_no_split_escaped_more_escapes(self):
        self.assertEqual(split('"foo "   "bar "" quux" baz " peng"""'),
                              ('"foo "', '"bar "', '" quux"', 'baz', '" peng"', '""'))


class SingleQuoteSplitTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(split("'foo bar'"), ("'foo bar'",))

    def test_more_spaces(self):
        self.assertEqual(split("'foo bar baz peng'"), ("'foo bar baz peng'",))

    def test_startswith_space(self):
        self.assertEqual(split("' foo'"), ("' foo'",))

    def test_endswith_space(self):
        self.assertEqual(split("'foo '"), ("'foo '",))

    def test_double_space(self):
        self.assertEqual(split("'foo  bar'"), ("'foo  bar'",))

    def test_substring(self):
        self.assertEqual(split("foo bar 'baz peng'"), ("foo", "bar", "'baz peng'",))

    def test_substring_double_space(self):
        self.assertEqual(split("foo 'bar baz'  peng"), ("foo", "'bar baz'", "peng",))

    def test_substring_triple_space(self):
        self.assertEqual(split("foo   'bar baz' peng"), ("foo", "'bar baz'", "peng",))

    def test_no_split_double_quote(self):
        self.assertEqual(split("foo 'bar \"baz' peng"), ("foo", "'bar \"baz'", "peng",))

    def test_startswith_escaped_double_quote(self):
        self.assertEqual(split("\\\"'foo bar 'quux ' baz peng"),
                              ('\\"', "'foo bar '", 'quux', "' baz peng"))

    def test_endswith_escaped_double_quote(self):
        self.assertEqual(split("'foo bar 'quux ' baz peng\\\""),
                              ("'foo bar '", 'quux', '\' baz peng\\"'))

    def test_no_split_escaped(self):
        self.assertEqual(split("foo 'bar \\'quux\\' baz' peng"),
                              ('foo', "'bar \\'", "quux\\'", 'baz', "' peng"))

    def test_no_split_escaped_more_spaces(self):
        self.assertEqual(split("foo ' bar \\'quux \\' baz' peng"),
                              ('foo', "' bar \\'", 'quux', "\\'", 'baz', "' peng"))

    def test_startswith_escaped(self):
        self.assertEqual(split("\\'foo bar 'quux ' baz peng"),
                              ("\\'foo", "bar", "'quux '", "baz", "peng",))

    def test_unquoted_spaces(self):
        self.assertEqual(split("\\'foo \\' bar ' quux '"),
                              ("\\'foo", "\\'", "bar", "' quux '",))

    def test_no_split_escaped_more_escapes(self):
        self.assertEqual(split("'foo '   'bar '' quux' baz ' peng'''"),
                              ("'foo '", "'bar '", "' quux'", 'baz', "' peng'", "''"))

    def test_evil_quoting(self):
        self.assertEqual(split("'foo bar'\\''baz ' peng"),
                              ("'foo bar'", "\\'", "'baz '", 'peng'))

