#!/usr/bin/env/python
#encoding:utf-8

from subprocess import Popen, PIPE
import re

from . import xmltodict

#TODO: turn numeric keys into ints n floats (height, width, bitrate n such)

class MediaInfoError(Exception):
    pass

class Track(object):
    def __init__(self, track_dict):
        for key, value in track_dict.iteritems():
            k = re.sub('\W+', '', key)
            self.__setattr__(k.lower(), value)

class MediaInfo(object):
    video = None
    audio = []
    general = None
    def __init__(self, filename):
        tracks = get_tracks(filename)
        for t in tracks:
            if t.type == 'Video':
                self.video = t
            elif t.type == 'Audio':
                self.audio.append(t)
            elif t.type == 'General':
                self.general = t
            

def get_raw_xml(filename):
    """
    Get raw mediainfo output for given filename.
    """
    p = Popen(
        ['mediainfo', '--output=XML', filename],
        stdout=PIPE
        )
    out, err = p.communicate()
    if err:
        raise MediaInfoError(err)
    else:
        return out

def get_dict(filename):
    d = xmltodict.parse(
        get_raw_xml(filename)
        )
    return d['Mediainfo']['File']

def get_tracks(filename):
    """
    get_tracks(filename) ->> Track(s)
    yield the mediainfo tracks as Track objects.
    """
    for t in get_dict(filename)['track']:
        yield Track(t)
        
    



    
    
