# -*- coding: utf-8 -*-

import unittest

from rl import completer
from rl import completion
from rl import generator
from rl import readline
from rl import print_exc

from gpgkeys.gpgkeys import GPGKeys
from gpgkeys.testing import JailSetup
from gpgkeys.testing import reset

from gpgkeys.completions.completion import backslash_quote
from gpgkeys.completions.completion import backslash_dequote
from gpgkeys.completions.completion import is_fully_quoted
from gpgkeys.completions.completion import dequote_string
from gpgkeys.completions.completion import quote_string
from gpgkeys.completions.completion import backslash_quote_string
from gpgkeys.completions.filename import dequote_filename
from gpgkeys.completions.filename import quote_filename
from gpgkeys.completions.filename import backslash_quote_filename

TAB = '\t'


@print_exc
@generator
def filecomplete(text):
    return completion.complete_filename(text)


class BackslashQuoteTests(unittest.TestCase):

    def setUp(self):
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()

    def test_backslash_quote(self):
        self.assertEqual(backslash_quote(''), '')
        self.assertEqual(backslash_quote(' '), '\\ ')
        self.assertEqual(backslash_quote('a'), 'a')
        self.assertEqual(backslash_quote('@'), '\\@')

    def test_backslash_quote_string(self):
        self.assertEqual(backslash_quote(' foo bar#baz&'), '\\ foo\\ bar\\#baz\\&')

    def test_backslash_quote_unknown_char(self):
        self.assertEqual(backslash_quote('€'), '€')


class BackslashDequoteTests(unittest.TestCase):

    def setUp(self):
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()

    def test_backslash_dequote(self):
        self.assertEqual(backslash_dequote(''), '')
        self.assertEqual(backslash_dequote(' '), ' ')
        self.assertEqual(backslash_dequote('\\ '), ' ')
        self.assertEqual(backslash_dequote('a'), 'a')
        self.assertEqual(backslash_dequote('\\@'), '@')

    def test_backslash_dequote_string(self):
        self.assertEqual(backslash_dequote('\\ foo\\ bar\\#baz\\&'), ' foo bar#baz&')

    def test_backslash_dequote_unknown_char(self):
        self.assertEqual(backslash_dequote('\\€'), '\\€') # NB: not dequoted


class FullyQuotedTests(unittest.TestCase):

    def setUp(self):
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()

    def test_fully_quoted(self):
        self.assertEqual(is_fully_quoted('foo\\ bar\\"baz\\&'), True)
        self.assertEqual(is_fully_quoted('foo\\ bar\\"baz\\\\'), True)

    def test_not_fully_quoted(self):
        self.assertEqual(is_fully_quoted('foo&bar'), False)
        self.assertEqual(is_fully_quoted('foo\\&bar\\'), False)


class FileSetup(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        self.mkfiles()

    def complete(self, text):
        completion.line_buffer = text
        readline.complete_internal(TAB)
        return completion.line_buffer

    def mkfiles(self):
        self.mkfile("Al'Hambra.txt")
        self.mkfile('Foo\\"Peng\\".txt')
        #self.mkfile('Foo\\Bar.txt')
        #self.mkfile('Foo\\Baz.txt')
        self.mkfile('Hello World.txt')
        #self.mkfile('Lee "Scratch" Perry.txt')
        #self.mkfile('Mädchen.txt')
        #self.mkfile('Simple.txt')
        self.mkfile('Tilde.tx~')
        self.mkfile('~StartsWithTilde.txt')


class DequoteStringTests(FileSetup):

    def setUp(self):
        FileSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        completer.completer = filecomplete
        completer.filename_dequoting_function = print_exc(dequote_string)
        completer.filename_quoting_function = lambda x,y,z: x

    def test_dequote_string(self):
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), 'Hello World.txt ')
        self.assertEqual(self.complete('Hello\\ '), 'Hello World.txt ')
        self.assertEqual(self.complete("Al\\'"), "Al'Hambra.txt ")
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\"Peng\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')

    def test_dequote_if_single_quote_default(self):
        completer.quote_characters = "'\""
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), 'Hello World.txt ')
        self.assertEqual(self.complete('Hello\\ '), 'Hello World.txt ')
        self.assertEqual(self.complete("Al\\'"), "Al'Hambra.txt ")
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\"Peng\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')


class QuoteStringTests(FileSetup):

    def setUp(self):
        FileSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        completer.completer = filecomplete
        completer.filename_dequoting_function = print_exc(dequote_string)
        completer.filename_quoting_function = print_exc(quote_string)

    def test_quote_string(self):
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), '"Hello World.txt" ')
        self.assertEqual(self.complete('Hello\\ '), '"Hello World.txt" ')
        self.assertEqual(self.complete("Al\\'"), '''"Al'Hambra.txt" ''')
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\\\\\"Peng\\\\\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')

    def test_user_quote_string(self):
        self.assertEqual(self.complete('"'), '"')
        self.assertEqual(self.complete('"Hello'), '"Hello World.txt" ')
        self.assertEqual(self.complete('"Hello '), '"Hello World.txt" ')
        self.assertEqual(self.complete("\"Al'"), '''"Al'Hambra.txt" ''')
        self.assertEqual(self.complete('"Foo\\\\\\"'), '"Foo\\\\\\"Peng\\\\\\".txt" ')
        self.assertEqual(self.complete('"Tilde.tx\\~'), '"Tilde.tx~" ')
        self.assertEqual(self.complete('"~'), '"~StartsWithTilde.txt" ')

    def test_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('fun'), '"funny dir"/') # NB: slash appended by readline

    def test_user_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('"fun'), '"funny dir"/') # NB: slash appended by readline


class BackslashQuoteStringTests(FileSetup):

    def setUp(self):
        FileSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        completer.completer = filecomplete
        completer.filename_dequoting_function = print_exc(dequote_string)
        completer.filename_quoting_function = print_exc(backslash_quote_string)

    def test_backslash_quote_string(self):
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), 'Hello\\ World.txt ')
        self.assertEqual(self.complete('Hello\\ '), 'Hello\\ World.txt ')
        self.assertEqual(self.complete("Al\\'"), "Al\\'Hambra.txt ")
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\\\\\"Peng\\\\\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')

    def test_user_quote_string(self):
        self.assertEqual(self.complete('"'), '"')
        self.assertEqual(self.complete('"Hello'), '"Hello World.txt" ')
        self.assertEqual(self.complete('"Hello '), '"Hello World.txt" ')
        self.assertEqual(self.complete("\"Al'"), '''"Al'Hambra.txt" ''')
        self.assertEqual(self.complete('"Foo\\\\\\"'), '"Foo\\\\\\"Peng\\\\\\".txt" ')
        self.assertEqual(self.complete('"Tilde.tx\\~'), '"Tilde.tx~" ')
        self.assertEqual(self.complete('"~'), '"~StartsWithTilde.txt" ')

    def test_backslash_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('fun'), 'funny\\ dir/') # NB: slash appended by readline

    def test_user_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('"fun'), '"funny dir"/') # NB: slash appended by readline


class DequoteFilenameTests(FileSetup):

    def setUp(self):
        FileSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        completer.completer = filecomplete
        completer.filename_dequoting_function = print_exc(dequote_filename)
        completer.filename_quoting_function = lambda x,y,z: x

    def test_dequote_filename(self):
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), 'Hello World.txt ')
        self.assertEqual(self.complete('Hello\\ '), 'Hello World.txt ')
        self.assertEqual(self.complete("Al\\'"), "Al'Hambra.txt ")
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\"Peng\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')

    def test_dequote_if_single_quote_default(self):
        completer.quote_characters = "'\""
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), 'Hello World.txt ')
        self.assertEqual(self.complete('Hello\\ '), 'Hello World.txt ')
        self.assertEqual(self.complete("Al\\'"), "Al'Hambra.txt ")
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\"Peng\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')


class QuoteFilenameTests(FileSetup):

    def setUp(self):
        FileSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        completer.completer = filecomplete
        completer.filename_dequoting_function = print_exc(dequote_filename)
        completer.filename_quoting_function = print_exc(quote_filename)

    def test_quote_filename(self):
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), '"Hello World.txt" ')
        self.assertEqual(self.complete('Hello\\ '), '"Hello World.txt" ')
        self.assertEqual(self.complete("Al\\'"), '''"Al'Hambra.txt" ''')
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\\\\\"Peng\\\\\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')

    def test_user_quote_filename(self):
        self.assertEqual(self.complete('"'), '"')
        self.assertEqual(self.complete('"Hello'), '"Hello World.txt" ')
        self.assertEqual(self.complete('"Hello '), '"Hello World.txt" ')
        self.assertEqual(self.complete("\"Al'"), '''"Al'Hambra.txt" ''')
        self.assertEqual(self.complete('"Foo\\\\\\"'), '"Foo\\\\\\"Peng\\\\\\".txt" ')
        self.assertEqual(self.complete('"Tilde.tx\\~'), '"Tilde.tx~" ')
        self.assertEqual(self.complete('"~'), '"~StartsWithTilde.txt" ')

    def test_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('fun'), '"funny dir/') # NB: No closing quote on dir

    def test_user_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('"fun'), '"funny dir/') # NB: no closing quote on dir


class BackslashQuoteFilenameTests(FileSetup):

    def setUp(self):
        FileSetup.setUp(self)
        reset()
        self.cmd = GPGKeys()
        self.cmd.init_completer()
        completer.completer = filecomplete
        completer.filename_dequoting_function = print_exc(dequote_filename)
        completer.filename_quoting_function = print_exc(backslash_quote_filename)

    def test_backslash_quote_filename(self):
        self.assertEqual(self.complete(''), '')
        self.assertEqual(self.complete('Hello'), 'Hello\\ World.txt ')
        self.assertEqual(self.complete('Hello\\ '), 'Hello\\ World.txt ')
        self.assertEqual(self.complete("Al\\'"), "Al\\'Hambra.txt ")
        self.assertEqual(self.complete('Foo\\\\\\"'), 'Foo\\\\\\"Peng\\\\\\".txt ')
        self.assertEqual(self.complete('Tilde.tx\\~'), 'Tilde.tx~ ')
        self.assertEqual(self.complete('\\~'), '~StartsWithTilde.txt ')

    def test_user_quote_filename(self):
        self.assertEqual(self.complete('"'), '"')
        self.assertEqual(self.complete('"Hello'), '"Hello World.txt" ')
        self.assertEqual(self.complete('"Hello '), '"Hello World.txt" ')
        self.assertEqual(self.complete("\"Al'"), '''"Al'Hambra.txt" ''')
        self.assertEqual(self.complete('"Foo\\\\\\"'), '"Foo\\\\\\"Peng\\\\\\".txt" ')
        self.assertEqual(self.complete('"Tilde.tx\\~'), '"Tilde.tx~" ')
        self.assertEqual(self.complete('"~'), '"~StartsWithTilde.txt" ')

    def test_backslash_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('fun'), 'funny\\ dir/')

    def test_user_quote_directory(self):
        self.mkdir('funny dir')
        self.assertEqual(self.complete('"fun'), '"funny dir/') # NB: no closing quote on dir

