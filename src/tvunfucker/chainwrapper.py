import tvdb_api

import tvunfucker

import dirscanner
import parser
import tvdbwrapper



log = tvunfucker.log
api = tvdb_api.Tvdb(apikey=tvunfucker.tvdb_key)


def get_parsed_episodes(source):
    """
    Yields LocalEpisode objects in given source directory
    which have gone through all possible/required parse attempts.
    """
    for eppath in dirscanner.get_episodes(source):
        ep = parser.ez_parse_episode(eppath)
        if ep.is_fully_parsed():
            yield ep
            continue
        yield parser.reverse_parse_episode(eppath, source)


def tvdb_lookup(ep):
    """
    LocalEpisode -> LocalEpisode (the same one)\n
    Look up the given ep with the tvdb api and attach the resulting
    tvdb_api.Episode object to it's 'tvdb_ep' key.    
    """
    if not ep.is_fully_parsed():
        return ep
    series = tvdbwrapper.get_series(ep.clean_name(ep['series_name']), api)
    if not series:
        return ep
    webep = series[ep['season_num']][ep['ep_num']]
    ep['tvdb_ep'] = webep
    return ep


#TODO: Move this somewhere more appropriate
class EpisodeSource(dict):
    def __init__(self, sourcedir):
        self.source_dir = sourcedir
        super(EpisodeSource, self).__init__()

def main():
    unparsed = []
    source = EpisodeSource('/home/steini/tvtesttree')
    for ep in get_parsed_episodes(source.source_dir):
        webep = None
        #print ep['path']
        try:
            tvdb_lookup(ep)
        except tvdb_api.tvdb_shownotfound as e:
            log.error(e.message)
            unparsed.append(ep)
        except tvdb_api.tvdb_seasonnotfound as e:
            log.error(e.message)
            unparsed.append(ep)
        except tvdb_api.tvdb_episodenotfound as e:
            log.error(e.message)
            unparsed.append(ep)  
        else:
            source[ep['path']] = ep            
