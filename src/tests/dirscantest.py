import logging
import os

from tvunfucker import dirscanner

dirscanner.log.setLevel(logging.DEBUG)


sdir = os.path.join(
    os.path.dirname(__file__), 
    'testdata/testfs'
    )

[x for x in dirscanner.get_episodes(sdir)]
