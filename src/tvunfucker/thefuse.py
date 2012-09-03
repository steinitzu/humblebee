import logging
from collections import defaultdict


import llfuse


log = logging.getLogger('tvunfucker')

class VirtualLinker(llfuse.Operations):

    def __init__(self, realdir):
        llfuse.Operations.__init__(self)
        self.real_dir = realdir
        self.inode_open_count = defaultdict(int)


    def create(self, inode_parent, name, mode, ctx):
        
