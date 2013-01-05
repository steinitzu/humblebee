from __future__ import division

from .mediainfo import MediaInfo

#codecs in order of worst to best (lower case it)
codecs = [
    'mpeg',
    'xvid',
    'avc',
]
    

def _is_video_file(minfo):
    """
    is_video_file(MediaInfo) -> bool
    """
    return minfo.video is not None



def get_better_episode(ep1, ep2):
    """
    get_better_episode(Episode, Episode) -> Episode
    Give two episodes and return the one which appears 
    to be of better quality.    
    
    Useful to treat duplicates.
    """
    m1points = 0
    m2points = 0
    m1 = MediaInfo(ep1['file_path'])
    m2 = MediaInfo(ep2['file_path'])

    v1 = m1.video
    v2 = m2.video
    if v1.dict == v2.dict:
        #they are the same
        return None

    m1res = v1.height*m1.video.width
    m2res = v2.height*m2.video.width    

    if m1res > m2res: 
        m1points+=1
    elif m2res > m1res: 
        m2points+=1
    
    if v1.bit_rate > v2.bit_rate:
        m1points+=1
    elif v2.bit_rate > v1.bit_rate:
        m2points+=1
    

    #check which ep is longer
    #if one is more than 10% longer, the other probably has some bits missing
    #so longer one automatically wins
    d1 = v1.duration.seconds
    d2 = v2.duration.seconds
    if d2/(d2+d1)*100 < 40:
        return ep1 #K.O. it's more than 10% longer
    elif d1/(d1+d2)*100 < 40:
        return ep2

    if m1points==m2points:
        #final round
        
