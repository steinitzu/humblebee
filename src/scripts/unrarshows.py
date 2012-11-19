#!/usr/bin/python

import os, logging, sys
from glob import glob

from tvunfucker import dirscanner
import logmake


log = logging.getLogger('scriptlog')


def main(tvdir):
    log.setLevel(logging.DEBUG)
    direps = [
        ep for ep in 
        dirscanner.get_episodes(tvdir)
        if os.path.isdir(ep)
        ]
    rareps = []    
    oneglob = []
    for ep in direps:
        os.chdir(ep)
        globr1 = glob('*.r01')
        globrar = glob('*.rar')
        #log.debug('%s: %s, %s', ep, globrar, globr1)
        if globrar and globr1:
            rareps.append(ep)
            log.info(
                'Found rarred episode: %s', 
                os.path.relpath(ep, start=tvdir)
                )
        if (globr1 or globrar) and (not globrar or not globr1):
            log.info(
                'Found half-rarred episode: %s', 
                os.path.relpath(ep, start=tvdir)
                )            
            oneglob.append(ep)
    #log.debug('\n'.join(e for e in oneglob))
    log.info('There were %s rared episodes.', len(rareps))    
    log.info('There were %s singleglob episodes.', len(oneglob))    

if __name__ == "__main__":
    main(sys.argv[1])

