#!/usr/bin/env python
#
#  XXX  Identifying information about tests here.
#
#===============
#  This is based on a skeleton test file, more information at:
#
#     https://github.com/linsomniac/python-unittest-skeleton

import unittest, os

from tvunfucker import parser, tvdbwrapper, dbguy

class test_Parser(unittest.TestCase):
    @classmethod
    def setUp(self):
        ###  XXX code to do setup
        self.cwd = os.path.dirname(__file__)

    def tearDown(self):
        ###  XXX code to do tear down
        pass

    def test_localepisode_setitem(self):
        ep = dbguy.Episode('')
        tnum = 23451
        for key in ep.numeric_keys:
            with self.assertRaises(ValueError):
                ep[key] = 'invalidinteger'
        for key in ep.numeric_keys:
            ep[key] = tnum
            self.assertEqual(ep[key], tnum)

        for key in ep.preset_keys:
            if key in ep.numeric_keys:
                continue
            ep[key] = 'fuckthisshit'
            self.assertEqual(ep[key], 'fuckthisshit')

    def test_ez_parse_scene(self):
        fname = os.path.join(
            self.cwd,
            'testdata/testfs/Reaper/Reaper s01/reaper.s01e06.hdtv.xvid-xor.avi'
            )
        ep = parser.ez_parse_episode(fname)
        self.assertEqual(ep['series_title'], 'reaper')
        self.assertEqual(ep['ep_number'], 6)
        self.assertEqual(ep['season_number'], 1)

    def test_basic_lookup(self):
        ename = '30.Rock.S06E06E07.HDTV.XviD-LOL'
        ep = parser.ez_parse_episode(ename)
        epp = tvdbwrapper.lookup(ep)
        print '\n'.join(
            ['%s : %s' % (k,v) for k,v in epp.iteritems()]
            )
        
    def test_reverse_parse(self):
        raise NotImplementedError

unittest.main()
