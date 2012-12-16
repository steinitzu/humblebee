#!/usr/bin/env python

import unittest, os

from tvunfucker import dbguy

class test_XXX_Test_Group_Name(unittest.TestCase):
    @classmethod
    def setUp(self):
        ###  XXX code to do setup
        tvdir = os.path.join(
            __file__, 
            'testdata/testfs'
            )
        self.db = dbguy.TVDatabase(tvdir)

    def tearDown(self):
        ###  XXX code to do tear down
        pass

    def test_XXX_Test_Name(self):
        raise NotImplementedError('Insert test code here.')
        #  Examples:
        # self.assertEqual(fp.readline(), 'This is a test')
        # self.assertFalse(os.path.exists('a'))
        # self.assertTrue(os.path.exists('a'))
        # self.assertTrue('already a backup server' in c.stderr)
        # with self.assertRaises(Exception):
        #    raise Exception('test')
        # self.assertIn('fun', 'disfunctional')

    def test_initialize_tvdb(self):
        """
        Initialize a non existing local tv database with schema.
        """
        

unittest.main()
