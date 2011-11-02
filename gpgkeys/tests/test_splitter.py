import unittest

from rl import completer
from kmd.completions import quoting

from gpgkeys.scanner import char_is_quoted
from gpgkeys.splitter import Token, T_WORD
from gpgkeys.splitter import split
from gpgkeys.testing import reset


class TokenTests(unittest.TestCase):

    def test_create_token(self):
        t = Token('foo', 0, 3, T_WORD)
        self.assertTrue(isinstance(t, Token))
        self.assertEqual(t, 'foo')
        self.assertEqual(t.start, 0)
        self.assertEqual(t.end, 3)
        self.assertEqual(t.type, T_WORD)

    def test_add_str(self):
        t = Token('foo', 0, 3, T_WORD)
        t = t + 'bar'
        self.assertTrue(isinstance(t, Token))
        self.assertEqual(t, 'foobar')
        self.assertEqual(t.start, 0)
        self.assertEqual(t.end, 3)
        self.assertEqual(t.type, T_WORD)

    def test_add_assign_str(self):
        t = Token('foo', 0, 3, T_WORD)
        t += 'bar'
        self.assertTrue(isinstance(t, Token))
        self.assertEqual(t, 'foobar')
        self.assertEqual(t.start, 0)
        self.assertEqual(t.end, 3)
        self.assertEqual(t.type, T_WORD)

    def test_add_token(self):
        t = Token('foo', 0, 3, T_WORD)
        t = t + Token('bar', 12, 15, T_WORD)
        self.assertTrue(isinstance(t, Token))
        self.assertEqual(t, 'foobar')
        self.assertEqual(t.start, 0)
        self.assertEqual(t.end, 3)
        self.assertEqual(t.type, T_WORD)

    def test_turns_into_str_otherwise(self):
        t = Token('foo', 0, 3, T_WORD)
        s = t.lower()
        self.assertFalse(isinstance(s, Token))
        self.assertTrue(isinstance(s, str))


class CharIsQuotedTests(unittest.TestCase):

    TRUE = (
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
        '\'foo\\\'"\'',
        '\'foo"\'"\'',
    )

    FALSE = (
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
        '\'foo\'\'',
        '\'foo\\\'\'',
        '\'foo"\'\'',
        '\'foo\\\'\'\'',
        # The closing quote character is NOT quoted
        '\'foo"\'\'\'',
        '"foo \'bar\'"',
        '\'foo "bar"\'',
    )

    def setUp(self):
        reset()
        completer.quote_characters = '"\''

    def test_true(self):
        # Expect the last character in s to be quoted
        for s in self.TRUE:
            self.assertEqual(char_is_quoted(s, len(s)-1), True, 'not True: %r' % s)

    def test_false(self):
        # Expect the last character in s to be unquoted
        for s in self.FALSE:
            self.assertEqual(char_is_quoted(s, len(s)-1), False, 'not False: %r' % s)

    def test_true_quoting(self):
        # Expect the last character in s to be quoted
        for s in self.TRUE:
            self.assertEqual(quoting.char_is_quoted(s, len(s)-1), True, 'not True: %r' % s)

    def test_false_quoting(self):
        # Expect the last character in s to be unquoted
        for s in self.FALSE:
            self.assertEqual(quoting.char_is_quoted(s, len(s)-1), False, 'not False: %r' % s)


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
                              ("'foo bar'\\''baz '", 'peng'))

