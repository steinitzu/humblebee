import logging

from romdb import tvdirparser
from romdb.romlog import *


def non_destructive_test():
    tvdirparser.scan_tv_source('/media/boneraper/+incoming')

if __name__ == "__main__":
    rom_log.setLevel(logging.DEBUG)
    non_destructive_test()
