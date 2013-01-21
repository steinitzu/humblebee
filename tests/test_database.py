#!/usr/bin/env python

import unittest, os

from testprep import log

from humblebee import dbguy, parser, tvdbwrapper

class test_Database(unittest.TestCase):
    @classmethod
    def setUp(self):
        ###  XXX code to do setup
        tvdir = os.path.join(
            os.path.dirname(__file__), 
            'testdata/testfs'
            )
        self.db = dbguy.TVDatabase(tvdir)
        try:
            os.unlink(self.db.dbfile)
        except: pass

    def tearDown(self):
        ###  XXX code to do tear down
        os.unlink(self.db.dbfile)

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

    def test_get_episodes(self):
        """
        also tests upsert.
        """
        self.db.create_database()
        ep = parser.base_parse_episode(
            os.path.join(
                self.db.directory,
                'Sons of Anarchy/S04/Sons.of.'\
                +'Anarchy.S04E11.Call.of.Duty.PROPER.HDTV.XviD-FQM'\
                +'/sons.of.anarchy.s04e11.hdtv.xvid-fqm.avi'))
        ep = tvdbwrapper.lookup(ep)
        self.db.upsert_episode(ep)
        deps = self.db.get_episodes('WHERE season_number = ?', params=(4,))
        log.debug(deps)
        deps = [d for d in deps]
        self.failIfEqual(len(deps), 0)

        for e in deps:
            righttype = isinstance(e, dbguy.Episode)
            self.assertTrue(righttype)        
            self.assertEqual(e['season_number'], 4)

unittest.main(verbosity=2)
