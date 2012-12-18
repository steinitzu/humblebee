#!/usr/bin/env python

import unittest, os

from tvunfucker import dbguy

class test_Database(unittest.TestCase):
    @classmethod
    def setUp(self):
        ###  XXX code to do setup
        tvdir = os.path.join(
            os.path.dirname(__file__), 
            'testdata/testfs'
            )
        self.db = dbguy.TVDatabase(tvdir)

    def tearDown(self):
        ###  XXX code to do tear down
        os.unlink(self.db.dbfile)
    """
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
    """

    def test_initialize_existing_tvdb_error(self):
        """
        Try initializing an existing database file.
        Should raise a InitExistingDatabaseError.
        """        
        #create the db
        self.db.create_database()
        with self.assertRaises(dbguy.InitExistingDatabaseError):
            #should raise error
            self.db.create_database()

    def test_initialize_tvdb(self):
        """
        Initialize a non existing local tv database with schema.
        """
        self.db.create_database()

unittest.main(verbosity=2)
