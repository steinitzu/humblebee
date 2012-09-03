import logging
from collections import defaultdict


import llfuse


log = logging.getLogger('tvunfucker')

class VirtualLinker(llfuse.Operations):

    def __init__(self, database):
        llfuse.Operations.__init__(self)
        self.database = database
        self.inode_open_count = defaultdict(int)

    def access(self, inode, mode, ctx):
        return True


    def readdir(self, fh, off):
        log.debug(fh, off)
        for i in range(20):
            yield str(i)
        
