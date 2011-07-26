import unittest
import os

from os.path import isfile, expanduser, abspath

from rl import history

from gpgkeys.testing import JailSetup
from gpgkeys.testing import reset


class HistoryFileTests(JailSetup):
    # XXX You will lose your ~/.history file when you run these tests

    def setUp(self):
        JailSetup.setUp(self)
        reset()
        self.histfile = expanduser('~/.history')
        self.remove_histfile()

    def tearDown(self):
        self.remove_histfile()
        JailSetup.tearDown(self)

    def remove_histfile(self):
        if isfile(self.histfile):
            os.remove(self.histfile)

    def test_no_histfile(self):
        self.assertEqual(isfile(self.histfile), False)

    def test_write_relative(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history', raise_exc=True)
        self.assertTrue(isfile('my_history'))

    def test_read_relative(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history')
        history.clear()
        history.read_file('my_history', raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_abspath(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(abspath('my_history'), raise_exc=True)
        self.assertTrue(isfile('my_history'))
        self.assertTrue(isfile(abspath('my_history')))

    def test_read_abspath(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('my_history')
        history.clear()
        history.read_file(abspath('my_history'), raise_exc=True)
        self.assertEqual(len(history), 2)

    def test_write_tilde_expanded(self):
        history.append('fred')
        history.append('wilma')
        history.write_file('~/.history', raise_exc=True)
        self.assertTrue(isfile(self.histfile))

    def test_read_tilde_expanded(self):
        history.append('fred')
        history.append('wilma')
        history.write_file(self.histfile)
        history.clear()
        history.read_file('~/.history', raise_exc=True)
        self.assertEqual(len(history), 2)

