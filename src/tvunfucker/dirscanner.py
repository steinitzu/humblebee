#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob

import config, parser #from this package
from logger import *
from texceptions import *


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


def get_file_from_single_ep_dir(dir_):
    """
    Finds the media file in a given single episode directory.
    Returns a path.
    """    
    log.debug('Checking single ep dir: %s', dir_)
    vfiles = [f for f in _get_video_files(dir_)]
    if len(vfiles) == 1:
        log.debug('One media file found: %s', vfiles[0])
        return vfiles[0]
    elif len(vfiles) == 0:
        log.debug('No media file found in dir: %s. Returning dirname', dir_)
        return dir_
    #do something when more than 1 file in the dir
    log.debug('There was more than one media file in dir: %s', dir_)
    for f in vfiles:
        fname = os.path.split(f)[1]
        if 'sample' in fname.lower():
            continue
        else:
            return f
                    


def get_episodes(dir_):
    """
    Recursive function which yields episodes from dir_ and down.\n
    Returns strings, just paths.
    """
    if not os.path.isdir(dir_):
        raise InvalidArgumentError(
            '\'%s\' is not a valid directory.' % dir_
            )

    for subdir in _get_sub_directories(dir_):
        log.info('Probing directory \'%s\'' % subdir)
        if dir_is_single_ep(subdir):
            ret = get_file_from_single_ep_dir(subdir)            
            log.info('Found episode: %s', ret)
            yield ret
            continue
        for file_ in _get_video_files(subdir):
            log.info('Found video file: %s', file_)
            yield file_
        for result in get_episodes(subdir):
            yield result            
