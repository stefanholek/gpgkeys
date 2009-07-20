import os
import unittest
import readline

from os.path import dirname

from gpgkeys.gpgkeys import GPGKeys


class CompleterTests(unittest.TestCase):

    def setUp(self):
        self.cmd = GPGKeys()
        #self.cmd.init_completer_delims()
        #readline.set_completer(self.cmd.complete)
        os.chdir(dirname(__file__))

    def test_simple(self):
        print self.cmd.completefiles('test_esc', 'fdump test_esc', 6, 13)

