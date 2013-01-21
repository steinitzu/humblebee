#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
from fnmatch import fnmatch

from . import parser
from .parser import base_parse_episode
from . import appconfig as cfg
from logger import log
from .texceptions import InvalidArgumentError
from .util import normpath, bytestring_path

FILE_EXTENSIONS = cfg.get('scanner', 'match-extensions').split(',')

#TODO: use os.walk, symlinks and whatnot

def _is_video_file(fn):
    topfn = os.path.split(fn)[1]
    if not os.path.isfile(fn):
        return False
    elif is_clutter(fn):
        return False
    elif not os.path.splitext(fn)[1] in FILE_EXTENSIONS:
        return False    
    else:
        return True

def _get_video_files(dir_):
    """
    Generator function. Yields video files in given dir_\n
    yields absolute paths
    """
    for name in os.listdir(dir_):
        abspath = os.path.join(dir_,name)
        if not _is_video_file(abspath):
            continue
        yield abspath


def dir_is_single_ep(dir_):
    """
    str path -> bool
    """
    ep = parser.base_parse_episode(dir_)
    return ep.is_fully_parsed()


def get_file_from_single_ep_dir(dir_):
    """
    Finds the media file in a given single episode directory.
    Returns a path.
    If no media file is found it returns the directory it self.    
    """    
    log.debug('Checking single ep dir: %s', dir_)
    vfiles = [f for f in _get_video_files(dir_)]
    if len(vfiles) == 1:
        log.debug('One media file found: %s', vfiles[0])
        return vfiles[0]
    elif len(vfiles) == 0:
        log.debug('No media file found in dir: %s. Returning dirname', dir_)
        return None
    #do something when more than 1 file in the dir
    log.debug('There was more than one media file in dir: %s', dir_)
    for f in vfiles:
        fname = os.path.split(f)[1]
        #TODO: What if 'sample' is in the ep title or something?
        if 'sample' in fname.lower():
            continue
        else:
            return f


def is_rar(path):
    """
    is_rar(path) -> bool
    Checks whether given path contains a scene style 
    rarred episode (e.g. *.r01, *.r02,...)
    """  
    rnumfiles = glob(
        os.path.join(path, '*.r[0-9][0-9]')
        )
    if rnumfiles: return True
    else: return False

def dir_is_empty(path):
    return not os.listdir(path)

def is_clutter(filename):
    clutter = cfg.get('scanner', 'clutter').split(',')
    for pat in clutter:
        if fnmatch(filename, pat):
            return True    
    return False    

def is_noscan(filename):
    noscan = cfg.get('scanner', 'no-scan').split(',')
    for pat in noscan:
        if fnmatch(filename.lower(), pat.lower()):
            return True
    return False

def get_episodes(dir_):
    if not os.path.isdir(dir_):
        raise InvalidArgumentError(
            '\'%s\' is not a valid directory.' % dir_
            )
    dir_ = normpath(dir_)
    log.debug('Starting scrape on: "%s"', dir_)
    bs = bytestring_path
    for dirpath, dirnames, filenames in os.walk(dir_):
        dirpath = normpath(dirpath)
        p = os.path.split(dirpath)[1]
        if is_clutter(p) or is_noscan(p):
            continue
        log.debug('Walking path: %s', dirpath)
        for subdir in dirnames:
            subdir = bs(subdir)
            if is_clutter(subdir) or is_noscan(subdir):
                continue
            subdir = os.path.join(dirpath, subdir)
            if dir_is_empty(subdir):
                continue
            if dir_is_single_ep(subdir):
                ret = get_file_from_single_ep_dir(subdir)
                if ret:
                    log.info('Found episode: %s', ret)
                    yield base_parse_episode(ret, dir_)
                elif is_rar(subdir):
                    log.info('Found rar episode: %s', subdir)
                    yield base_parse_episode(subdir, dir_)
                else:
                    continue            
        for fn in filenames:
            if is_clutter(fn):
                continue
            fn = bs(fn)
            fn = os.path.join(dirpath, fn)
            if _is_video_file(fn):
                yield base_parse_episode(fn, dir_)
            else:
                continue
