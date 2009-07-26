import unittest

from gpgkeys.escape import escape
from gpgkeys.escape import unescape
from gpgkeys.escape import split
from gpgkeys.escape import startidx


class EscapeTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(escape('foo bar'), 'foo\\ bar')

    def test_more_spaces(self):
        self.assertEqual(escape('foo bar baz peng'), 'foo\\ bar\\ baz\\ peng')

    def test_startswith_space(self):
        self.assertEqual(escape(' foo'), '\\ foo')

    def test_endswith_space(self):
        self.assertEqual(escape('foo '), 'foo\\ ')

    def test_double_space(self):
        self.assertEqual(escape('foo  bar'), 'foo\\ \\ bar')

    def test_no_double_escape(self):
        self.assertEqual(escape('foo\\ bar'), 'foo\\ bar')

    def test_no_double_escape_even_if_partial(self):
        self.assertEqual(escape('foo\\ bar baz'), 'foo\\ bar baz')

    def test_no_tab_escape(self):
        self.assertEqual(escape('foo\tbar'), 'foo\tbar')


class UnescapeTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(unescape('foo\\ bar'), 'foo bar')

    def test_more_spaces(self):
        self.assertEqual(unescape('foo\\ bar\\ baz\\ peng'), 'foo bar baz peng')

    def test_startswith_space(self):
        self.assertEqual(unescape('\\ foo'), ' foo')

    def test_endswith_space(self):
        self.assertEqual(unescape('foo\\ '), 'foo ')

    def test_double_space(self):
        self.assertEqual(unescape('foo\\ \\ bar'), 'foo  bar')

    def test_no_double_unescape(self):
        self.assertEqual(unescape('foo bar'), 'foo bar')

    #def test_no_double_unescape_even_if_partial(self):
    #    self.assertEqual(unescape('foo\\ bar baz'), 'foo\\ bar baz')

    def test_unescape_if_partial(self):
        self.assertEqual(unescape('foo\\ bar baz'), 'foo bar baz')

    def test_no_tab_unescape(self):
        self.assertEqual(unescape('foo\\\tbar'), 'foo\\\tbar')


class SplitTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(split('foo bar'), ('foo', 'bar'))

    def test_more_spaces(self):
        self.assertEqual(split('foo bar baz peng'), ('foo', 'bar', 'baz', 'peng'))

    def test_startswith_space(self):
        self.assertEqual(split(' foo'), ('', 'foo'))

    def test_endswith_space(self):
        self.assertEqual(split('foo '), ('foo', ''))

    def test_double_space(self):
        self.assertEqual(split('foo  bar'), ('foo', '', 'bar'))

    def test_triple_space(self):
        self.assertEqual(split('foo   bar'), ('foo', '', '', 'bar'))

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
                              ('\\\'"foo bar "quux', '" baz peng',))

    def test_endswith_escaped_single_quote(self):
        self.assertEqual(split('"foo bar "quux " baz peng\\\''),
                              ('"foo bar "quux', '" baz peng\\\'',))

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
                              ('"foo "', '"bar "" quux"', 'baz', '" peng"""',))


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
                              ("\\\"'foo bar 'quux", "' baz peng",))

    def test_endswith_escaped_double_quote(self):
        self.assertEqual(split("'foo bar 'quux ' baz peng\\\""),
                              ("'foo bar 'quux", "' baz peng\\\"",))

    def test_no_split_escaped(self):
        self.assertEqual(split("foo 'bar \\'quux\\' baz' peng"),
                              ("foo", "'bar \\'quux\\' baz'", "peng",))

    def test_no_split_escaped_more_spaces(self):
        self.assertEqual(split("foo ' bar \\'quux \\' baz' peng"),
                              ("foo", "' bar \\'quux \\' baz'", "peng",))

    def test_startswith_escaped(self):
        self.assertEqual(split("\\'foo bar 'quux ' baz peng"),
                              ("\\'foo", "bar", "'quux '", "baz", "peng",))

    def test_unquoted_spaces(self):
        self.assertEqual(split("\\'foo \\' bar ' quux '"),
                              ("\\'foo", "\\'", "bar", "' quux '",))

    def test_no_split_escaped_more_escapes(self):
        self.assertEqual(split("'foo '   'bar '' quux' baz ' peng'''"),
                              ("'foo '", "'bar '' quux'", "baz", "' peng'''",))

    def test_evil_quoting(self):
        self.assertEqual(split("'foo bar'\\''baz ' peng"), ("'foo bar'\\''baz '", "peng",))


class StartIdxTests(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(startidx('foo'), 0)

    def test_more_spaces(self):
        self.assertEqual('foo bar baz peng'[12:], 'peng')
        self.assertEqual(startidx('foo bar baz peng'), 12)

    def test_startswith_space(self):
        self.assertEqual(startidx(' foo'), 1)

    def test_endswith_space(self):
        self.assertEqual(startidx('foo '), 4)

    def test_double_space(self):
        self.assertEqual(startidx('  foo'), 2)

    def test_no_split_escaped(self):
        self.assertEqual(startidx('foo\\ bar'), 0)

    def test_no_split_escaped_more_spaces(self):
        self.assertEqual('foo bar\\ baz peng'[13:], 'peng')
        self.assertEqual(startidx('foo bar\\ baz peng'), 13)

    def test_no_split_escaped_more_spaces_less_idx(self):
        self.assertEqual(startidx('foo bar\\ baz peng', 13), 13)

    def test_no_split_escaped_more_spaces_less_idx_2(self):
        self.assertEqual('foo bar\\ baz peng'[4:], 'bar\\ baz peng')
        self.assertEqual(startidx('foo bar\\ baz peng', 10), 4)

    def test_startswith_escaped(self):
        self.assertEqual(startidx('\\ foo'), 0)

    def test_endswith_escaped(self):
        self.assertEqual(startidx('foo\\ '), 0)

    def test_stop_at_os_sep(self):
        self.assertEqual(startidx('foo\\ /bar\\ baz'), 6)

    def test_startswith_os_sep(self):
        self.assertEqual(startidx('/foo\\ bar\\ baz'), 1)

    def test_endswith_os_sep(self):
        self.assertEqual(startidx('foo\\ bar\\ baz/'), 14)

    def test_index_out_of_range(self):
        self.assertEqual(startidx('foo\\ /bar\\ baz', 42), 6)

    def test_index_out_of_range_endswith_os_sep(self):
        self.assertEqual(startidx('foo\\ bar\\ baz/', 14), 14)


