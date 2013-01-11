from unittest import TestCase
import unittest
import os
import logging

from tvunfucker.importer import Importer
from tvunfucker.util import normpath, syspath
from tvunfucker.tvregexes import tv_regexes
from tvunfucker.parser import ez_parse_episode

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

testfsdir = syspath(os.path.join(__file__,'tests/testdata/testfs'))
    

d = {
    'standard_repeat' : 'seinfeld.s03e17e18.the.boyfriend',
    'fov_repeat' : 'seinfeld 3x17 3x18 the boyfriend',
    'stupid_acronyms' : 'abc-seinfeld.s03e17'
    }



class TestParseAndLookup(TestCase):

    def setUp(self):
        self.tvdir = testfsdir

    def _test_regex(self, rename, ep):
        dosername = (
            'standard_repeat',
            'fov_repeat',            
            )        
        doepnum = dosername+(
            'stupid_acronyms',
            )
        doeepnum = dosername
        dosnum = doepnum        
            
        self.assertEqual(rename, ep['which_regex'])

        if rename in dosername:
            sname = ep['series_title'].lower()        
            self.assertEqual(sname, 'seinfeld')
        if rename in dosnum:
            snum = ep['season_number']            
            self.assertEqual(snum, 3)
        if rename in doepnum:
            enum = ep['ep_number']
            eenum = ep['extra_ep_number']
        if rename in doeepnum:        
            self.assertEqual(eenum, 18)

    def test_regexes(self):        
        #ut = unittest
        #regx = {}
        #for r in tv_regexes:
        #    regx[r.alias] = r.pattern
        for regn, fn in d.iteritems():
            ep = ez_parse_episode(fn)
            log.debug('Passed re: %s', regn)



if __name__ == '__main__':
    unittest.main()
    
