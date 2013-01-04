from .mediainfo import MediaInfo

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

    if v1.duration > v2.duration:
        m1points+=3
    elif v2.duration > v1.duration:
        m2points+=3
