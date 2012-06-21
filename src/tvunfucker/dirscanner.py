import os

import config, parser #from this package
from logger import *
from exceptions import *


#these functions belong to the world

def _get_sub_directories(dir_):
    """
    A generator functions which yields first level sub
    directories in the given dir_.\n
    Ignores dirs in ignored_dirs.\n
    yields absolute paths.
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if os.path.isfile(abspath):
            continue
        if name in config.ignored_dirs:            
            log.info('ignored dir in ignore list \'%s\'' % abspath)
            continue
        yield abspath

def _get_video_files(dir_):
    """
    Generator function. Yields video files in given dir_\n
    yields absolute paths
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if not os.path.isfile(abspath):
            continue
        if name in config.ignored_files:
            log.info('ignored file in ignore list \'%s\'' % abspath)
            continue
        ext = os.path.splitext(name)[1]
        if not ext in config.video_files:
            #TODO: do something about rar files
            continue
        yield abspath


def dir_is_single_ep(dir_):
    """
    str path -> bool
    """
    ep = parser.ez_parse_episode(dir_)
    return ep.is_fully_parsed()


def get_episodes(dir_):
    """
    Recursive function which yields episodes from dir_ and down.
    """
    if not os.path.isdir(dir_):
        raise InvalidArgumentError(
            '\'%s\' is not a valid directory.' % dir_
            )

    for subdir in _get_sub_directories(dir_):
        log.debug('Probing directory \'%s\'' % subdir)
        if dir_is_single_ep(subdir):
            yield subdir
            continue
        for file_ in _get_video_files(subdir):
            yield file_
        for result in get_episodes(subdir):
            yield result            


def main():

    scanner = SourceScanner('/home/steini/tvtesttree')
    a = scanner.get_episodes(scanner.source_dir)
    l = [i for i in a]
    #print '\n'.join([i for i in l])
    print len(l)    
    #print '\n'.join([a for a in scanner.get_episodes(scanner.source_dir)])



if __name__ == '__main__':
    main()
    
    
