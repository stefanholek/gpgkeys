import unittest
import os
import tempfile
import shutil

from os.path import realpath, isdir


class JailSetup(unittest.TestCase):

    origdir = None
    tempdir = None

    def setUp(self):
        self.origdir = os.getcwd()
        self.tempdir = realpath(tempfile.mkdtemp())
        os.chdir(self.tempdir)

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        if self.origdir is not None:
            if isdir(self.origdir):
                os.chdir(self.origdir)
        if self.tempdir is not None:
            if isdir(self.tempdir):
                shutil.rmtree(self.tempdir)


class TreeSetup(JailSetup):

    def setUp(self):
        JailSetup.setUp(self)
        try:
            os.mkdir('normaldir')
            os.chdir('normaldir')
            self.mkfile('"FOAD_World"')
            self.mkfile('"Goodbye_World".txt')
            self.mkfile('"Hello World".gif')
            self.mkfile('"Hello World".txt')
            self.mkfile("Al'Hambra.txt")
            self.mkfile('Foo\\"Peng\\".txt')
            self.mkfile('Foo\\Bar.txt')
            self.mkfile('Foo\\Baz.txt')
            self.mkfile('Hello World.txt')
            self.mkfile('Lee "Scratch" Perry.txt')
            self.mkfile('Simple.txt')
            os.chdir(os.pardir)
        except:
            self.cleanUp()
            raise

    def mkfile(self, filename):
        f = open(filename, 'wt')
        try:
            f.write('foo\n')
        finally:
            f.close()

