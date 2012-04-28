import logging

from romdb import tvdirparser
from romdb.romlog import *


def non_destructive_test():

    scanner = tvdirparser.TVSourceScanner('/media/boneraper/+incoming')
    scanner.scan_tv_source()
    rom_log.info('\nPROPER EPS\n\n')
    [rom_log.info(ep) for ep in scanner.proper_episodes]
    rom_log.info( '\n\nUNPARSABLE EPS\n')
    [rom_log.info(ep) for ep in scanner.unparseable_eps]
    rom_log.info('\n\nSINGLE EP DIRS\n')
    [rom_log.info(ep) for ep in scanner.single_ep_dirs]

    test_log.info('Number of proper_episodes = %d' % len(scanner.proper_episodes))
    test_log.info('Number of unparseable_eps = %d' % len(scanner.unparseable_eps))
    test_log.info('Number of single_ep_dirs = %d' % len(scanner.single_ep_dirs))    

    
    

if __name__ == "__main__":
    rom_log.setLevel(logging.DEBUG)
    non_destructive_test()
