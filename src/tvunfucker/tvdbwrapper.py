#!/usr/bin/env python
# -*- coding: utf-8 -*-

#builtin
import time
import logging
import sys

#3dparty
from tvdb_api import tvdb_error, Tvdb, tvdb_shownotfound, tvdb_seasonnotfound, tvdb_episodenotfound

#this pkg
from texceptions import ShowNotFoundError
import tvunfucker
import cfg

log = logging.getLogger('tvunfucker')

#tiss a ssingleton
_api = None

def get_api():
    #THERE Can be only one.... api
    global _api
    _api = Tvdb(apikey=tvunfucker.tvdb_key, actors=True)
    return _api

def get_series(series_name, api=None):
    """
    get_series(str) -> tvdb_api.Show\n
    raises tvdb_error or ShowNotFoundError on failure
    """
    api = get_api() if not api else api
    api = get_api()
    rtrc = 0
    series = None
    rtlimit = cfg.get('tvdb', 'retry_limit', int)
    rtinterval = cfg.get('tvdb', 'retry_interval', int)    

    while True:
        try:
            series = api[series_name]
        except tvdb_error as e:
            #probably means no connection
            if rtrc >= config.tvdb_retry_limit:
                raise
            log.warning(
                'Failed to connect to the tvdb. Retrying in %s seconds.',
                rtlimit
                )            
            time.sleep(rtlimit)
        except tvdb_shownotfound as e:
            #raise ShowNotFoundError(series_name)
            raise ShowNotFoundError(series_name), None, sys.exc_info()[2]
        else:
            break
    return series


def lookup(ep):
    """
    lookup(parser.LocalEpisode) -> The same LocalEpisode (just for fun)\n
    Finds the local ep more online, for more info.\n
    Raises SeasonNotFoundError and EpisodeNotFoundError
    """
    if not ep.is_fully_parsed():
        return None
    series = get_series(e.clean_name(ep['series_name']))
    log.info('Looking up series: %s', series)
    webep = None
    try:
        webep = series[ep['season_num']][ep['ep_num']]
    except tvdb_seasonnotfound as e:
        raise SeasonNotFoundError(
            series['seriesname'], ep['season_num']), None, sys.exec_info()[2]
    except tvdb_episodenotfound as e:
        raise EpisodeNotFoundError(
            series['seriesname'], ep['season_num'], ep['ep_num']), None, sys.exec_info()[2]
    else:
        return webep
    
    
    
