import unittest

from gpgkeys.splitter import Token, T_WORD
from gpgkeys.splitter import split
from gpgkeys.splitter import closequote


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

    def test_add_assign_token(self):
        t = Token('foo', 0, 3, T_WORD)
        t += Token('bar', 12, 15, T_WORD)
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


class SplitDoubleQuoteTests(unittest.TestCase):

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

    #def test_strip_quotes(self):
    #    self.assertEqual(split('"foo bar"', True), ('foo bar',))

    #def test_strip_quotes_more_quotes(self):
    #    self.assertEqual(split('"foo "   "bar "" quux" baz " peng"""', True),
    #                          ('foo ', 'bar ', ' quux', 'baz', ' peng', ''))


class SplitSingleQuoteTests(unittest.TestCase):

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

    #def test_strip_quotes(self):
    #    self.assertEqual(split("'foo bar'", True), ("foo bar",))

    #def test_strip_quotes_more_quotes(self):
    #    self.assertEqual(split("'foo '   'bar '' quux' baz ' peng'''", True),
    #                          ("foo ", "bar ", " quux", 'baz', " peng", ""))


class CloseQuoteTests(unittest.TestCase):

    def test_close_single_quote(self):
        t = Token("'foo", 0, 5, T_WORD)
        self.assertEqual(closequote((t,)), ("'foo'",))

    def test_close_double_quote(self):
        t = Token('"foo', 0, 5, T_WORD)
        self.assertEqual(closequote((t,)), ('"foo"',))

    def test_close_last_only(self):
        t = Token('"foo', 0, 5, T_WORD)
        self.assertEqual(closequote((t, t)), ('"foo', '"foo"'))

    def test_no_quotes(self):
        t = Token('foo', 0, 5, T_WORD)
        self.assertEqual(closequote((t,)), ('foo',))

