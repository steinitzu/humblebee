import unittest
import os
from tempfile import gettempdir
import shutil
import logging

from testprep import log

from humblebee.util import safe_rename
from humblebee.util import safe_make_dirs
from humblebee.util import make_symlink
from humblebee.util import samefile
from humblebee import logger





pj = os.path.join
class test_Util(unittest.TestCase):

    def setUp(self):
        self.testdir = os.path.join(
            gettempdir(), 'humble-bee-test'
            )
        safe_make_dirs(self.testdir)
        
    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_safe_rename(self):
        dest = pj(self.testdir, 'spam.txt')
        src = pj(self.testdir, 'eggs')
        f = open(dest, 'w')
        f.close()
        f = open(src, 'w')
        f.close()
        assert os.listdir(self.testdir) == ['eggs', 'spam.txt']
        safe_rename(src, dest)
        assert len(os.listdir(self.testdir)) == 2
        assert 'spam (1).txt' in os.listdir(self.testdir)

    def _make_file(self, fn):
        """
        Make an empty file with fn.
        """
        f = open(fn, 'w')
        f.close()

    def test_make_symlink(self):        
        target = pj(self.testdir, 'spam.avi')
        self._make_file(target)
        link = pj(self.testdir, 'eggs', 'milk', 'cakes', 'spam.lnk')
        make_symlink(target, link)
        log.debug('link: %s', link)
        assert os.path.exists(link)
        assert os.path.islink(link)
        assert samefile(os.path.realpath(link), target)


if __name__ == '__main__':
    unittest.main(verbosity=2)
