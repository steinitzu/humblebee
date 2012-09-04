import logging
from collections import defaultdict


import fuse


log = logging.getLogger('tvunfucker')

class VirtualLinker(llfuse.Operations):

    def __init__(self, database):
        llfuse.Operations.__init__(self)
        self.database = database
        self.inode_open_count = defaultdict(int)

    def access(self, inode, mode, ctx):
        return True

    def lookup(self, inode_parent, name):
        if name == '.':
            inode=inode_parent
        elif name == '..':
            inode = self.database


    def readdir(self, fh, off):
        log.debug(fh, off)
        for i in range(20):
            yield str(i)
        
