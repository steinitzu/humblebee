from __future__ import division

import os

from .mediainfo import MediaInfo
from .texceptions import InvalidVideoFileError

def quality_battle(ep1, ep2, source_dir):
    """
    quality_battle(Episode, Episode, source_dir) -> Episode or None
    For duplicate episodes.
    Checks which one is higher quality and return it.
    If both are of equal or similar enough quality None is returned.

    Uses a point system.
    1. video resolution -> 1 point
    2. video bitrate -> 1 point
    3. video duration -> 1 point if longer but less than 10% longer, 
       if more than 10% it's the winning point no matter what
    """

    m = (
        MediaInfo(ep1.path()),
        MediaInfo(ep2.path())
        )

    def raise_inv(plusmsg=''):
        raise InvalidVideoFileError(
            '"%s" and "%s" are not video files. '+plusmsg % 
            m[0].general.complete_name,
            m[1].general.complete_name
            )        

    points = [0, 0] #ep1, ep2
    ep = [ep1, ep2]
    if m[0].video and not m[1].video:
        return ep[0]
    elif m[1].video and not m[0].video:
        return ep[1]
    elif not m[1].video and not m[0].video:
        raise_inv('No video tracks.')
            
    if m[0].video.dict == m[1].video.dict:
        #they be the same, boy, lets bounce
        return

    res0 = m[0].video.height*m[0].video.width
    res1 = m[1].video.height*m[1].video.width

    if res0 > res1:
        points[0]+=1
    elif res1 > res0:
        points[1]+=1

    hasb = [True, True]
    try:
        b0 = m[0].video.bit_rate
    except AttributeError:
        hasb[0] = False
    try:
        b1 = m[1].video.bit_rate
    except AttributeError:
        hasb[1] = False
    if not hasb[0] and not hasb[1]:
        raise_inv('No bit_rate attribute')
    elif not hasb[0]:
        return ep[1]
    elif not hasb[1]:
        return ep[0]        

    if b0 > b1:
        points[0]+=1
    elif b1 > b0:
        points[1]+=1
    
    try:
        d0 = m[0].video.duration.seconds
    except AttributeError:
        d0 = m[0].general.duration.seconds
    try:
        d1 = m[0].video.duration.seconds
    except AttributeError:
        d1 = m[0].general.duration.seconds        
    if d1/(d1+d0)*100 < 40:
        return ep[0] #K.O. motherfucker
    elif d0/(d0+d1)*100 < 40:
        return ep[1]
    elif d0>d1:
        points[0]+=1
    elif d1>d0:
        points[1]+=1

    if points[0]>points[1]:
        return ep[0]
    elif points[1]>points[0]:
        return ep[1]
    elif points[1]==points[0]:
        return #fuck it, I tried

    

    


