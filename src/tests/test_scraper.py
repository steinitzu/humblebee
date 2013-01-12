from unittest import TestCase
import unittest
import os
import logging

from tvunfucker.importer import Importer
from tvunfucker.util import normpath, syspath
from tvunfucker.tvregexes import tv_regexes
from tvunfucker.parser import ez_parse_episode, reverse_parse_episode
from tvunfucker.tvdbwrapper import lookup

def get_log():
    l = logging.getLogger()
    if not l.handlers:
        logging.getLogger('tvunfucker').setLevel(logging.FATAL)
        l.addHandler(
            logging.StreamHandler()
            )
        l.setLevel(logging.DEBUG)
    return l

log = get_log()

testfsdir = syspath(
    normpath(os.path.join(os.path.dirname(__file__),'testdata/testfs'))
    )

###
#all the importer,parser,lookup, dbguy tests

class TestParseAndLookup(TestCase):

    def setUp(self):
        self.tvdir = testfsdir
        self.root = testfsdir

    def test_regexes(self):        
        """
        Test some of the filename regular expressions
        against known matching filenames.
        """
        d = {
            'standard' : 'seinfeld.s03e17e18.the.boyfriend-lol',
            'fov_repeat' : 'seinfeld 3x17 3x18 the boyfriend',
            'stupid_acronyms' : 'abc-seinfeld.s03e17',
            'verbose' : 'Seinfeld Season 03 Episode 17 The Boyfriend',
            #'scene_date_format' : 'seinfeld.1990.09.26.the.boyfriend' - borked
            'standardish_weird' : 'seinfelds03e17somecrap',
            'season_ep_only' : 'Season 3 Episode 17',    
            'stupid' : 'tpz-seinfeld317',
            }
        for regn, fn in d.iteritems():
            ep = ez_parse_episode(fn)
            log.debug('\n%s : %s', regn, fn)
            log.debug(ep.pretty())
            self._check_regex(regn, ep)
            log.debug('Passed re: %s', regn)

    def test_reverse_parse(self):
        fn = self._get_parsable(reverse=True)
        ep = reverse_parse_episode(fn, self.root)
        log.debug('\n'+ep.pretty())
        self.assertEqual(ep['series_title'], 'The War At Home')
        self.assertEqual(ep['season_number'], 1)
        self.assertEqual(ep['ep_number'], 11)

    def test_lookup(self):
        ep = reverse_parse_episode(
            self._get_parsable(True),
            self.root
            )
        lep = lookup(ep)
        self.assertEqual(lep['series_title'].lower(), 'the war at home')
        self.assertEqual(lep['season_number'], 1)
        self.assertEqual(lep['ep_number'], 11)
        
        


    def _get_parsable(self, reverse=True):
        if reverse:
            fn = 'The War At Home/Season 1/tpz-twat111.avi' 
            fn = os.path.join(self.root, fn)
            return fn
        else:
            raise NotImplementedError
        

    def _check_regex(self, rename, ep):
        dosername = (
            'standard',
            'fov_repeat',            
            'verbose',
            'standardish_weird',
            )        
        
        doepnum = (
            'standard',
            'fov_repeat',
            'stupid_acronyms',
            'verbose',
            'season_ep_only',
            'standardish_weird',
            'stupid',
            )
        dosnum = (
            'standard',
            'fov_repeat', 
            'stupid_acronym',
            'verbose',
            'season_ep_only',
            'standardish_weird',
            'stupid',
            )
        doeepnum = (
            'standard',
            'fov_repeat',
            )                    
        self.assertEqual(rename, ep['which_regex'])
        if rename in dosername:
            sname = ep.clean_name(ep['series_title']).lower()
            self.assertEqual(sname, 'seinfeld')
        if rename in dosnum:
            snum = ep['season_number']            
            self.assertEqual(snum, 3)
        if rename in doepnum:
            self.assertEqual(ep['ep_number'], 17)
        if rename in doeepnum:        
            self.assertEqual(ep['extra_ep_number'], 18)


        
        



if __name__ == '__main__':
    unittest.main()
    
