#!/usr/bin/env/python
#encoding:utf-8

"""
A python interface to mediainfo.
"""

from subprocess import Popen, PIPE
import re
from datetime import timedelta

import xmltodict

#TODO: turn numeric keys into ints n floats (height, width, bitrate n such)

class MediaInfoError(Exception):
    pass

class Track(object):
    """
    Info for a single track in a mediafile.
    Constructor accepts a dict created from mediainfo output.

    Member names will stripped of any non-alphanumeric and _ characters.
    """

    intkeys = ('bit_rate', 'height', 'width')
    def __init__(self, track_dict):
        for key, value in track_dict.iteritems():
            k = re.sub(r'\W+', '', key).lower()
            self.__setattr__(k, self._clean_value(k, value))

        self.dict = track_dict    

    def _clean_value(self, key, value):
        """
        Clean the given value corresponding to given key 
        and convert to correct type.
        """
        if key in self.intkeys:
            value = re.sub(r'[^0-9]*', '', value)
            return int(value)
        elif key == 'duration':
            return self._duration_to_time(value)
        else:
            return value

    def _duration_to_time(self, inst):
        """
        _duration_to_time(str) -> timedelta
        Convert a mediainfo duration string to timedelta.
        e.g. '2h 42mn' or '54mn 39s' or '30s 20ms'
        """
        timedict = {}
        for part in inst.split(' '):
            #part is like '22mn' or '2h' or '30s' or '600ms'
            if part[-1] == 'h':
                timedict['hours'] = int(part[:-1])
            elif part[-2:] == 'mn':
                timedict['minutes'] = int(part[:-2])
            elif part[-2:] == 'ms':
                timedict['milliseconds'] = int(part[:-2])
            elif part[-1] == 's':
                timedict['seconds'] = int(part[:-1])
            else:
                raise ValueError('%s is not a valid time value.' % part)
        return timedelta(**timedict)

class MediaInfo(object):

    def __init__(self, filename):
        tracks = get_tracks(filename)
        self.video = None
        self.audio = []
        self.general = None
        
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
    ts = get_dict(filename)['track']
    if isinstance(ts, dict):
        #there is only one track
        yield Track(ts)
    else:
        for t in get_dict(filename)['track']:            
            yield Track(t)

def get_mediainfo(filename):
    """
    get_mediainfo(filename) -> MediaInfo
    Returns a MediaInfo object with info for given filename.
    """
    return MediaInfo(filename)
        
    



    
    
