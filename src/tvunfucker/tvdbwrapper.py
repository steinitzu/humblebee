#!/usr/bin/env python
# -*- coding: utf-8 -*-

#builtin
import time, logging, sys, re

#3dparty
from tvdb_api.tvdb_api import tvdb_error, Tvdb, tvdb_shownotfound, tvdb_seasonnotfound, tvdb_episodenotfound

#this pkg
from .texceptions import ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError
from .texceptions import NoIdInURLError
import tvunfucker
from . import cfg
from .bingapi.bingapi import Bing

log = logging.getLogger('tvunfucker')

#tiss a ssingleton
_api = None

def get_api():
    #THERE Can be only one.... api
    global _api
    if not _api:
        _api = Tvdb(apikey=tvunfucker.tvdb_key, actors=True)
    return _api


def _imdb_id_from_url(url):
    """
    Parse the imdb id from an url like 'imdb.com/title/tt0092455'.
    """
    log.debug('URL: %s', url)
    m = re.search('title/(?P<id>tt\d{7})', url)  
    if not m:
        raise NoIdInURLError('No imdb id in url: %s' % url)
    return m.groupdict()['id']

def bing_lookup(series_name, api_key=None):
    """
    Uses bing to find the imdb id of the series.
    Accepts kwarg api_key, if None it will use the one from cfg.
    """
    if not api_key:
        api_key = cfg.get('bing', 'api-key')
    query = 'site:imdb.com %s' % series_name
    b = Bing(api_key, caching=True)
    sres = b.search(query)
    if not sres:
        raise ShowNotFoundError(
            'Series: \'%s\' was not found using bing',
            series_name, 
            )
    try:
        imdbid = _imdb_id_from_url(sres[0]['Url'])
    except NoIdInURLError as e:
        log.warning(e.message)
        raise ShowNotFoundError(
            'Series: \'%s\' was not found using bing',
            series_name, 
            ), None, sys.exc_info()[2]    
    api = get_api()
    try:
        series = api[imdbid, 'imdb']
    except tvdb_shownotfound:
        raise ShowNotFoundError(
            'Series: \'%s\' (imdb id: \'%s\' was not found.',
            series_name, 
            imdbid
            ), None, sys.exc_info()[2]    
    else:
        return series

def get_series(series_name, api=None):
    """
    get_series(str) -> tvdb_api.Show\n
    raises tvdb_error or ShowNotFoundError on failure
    """
    api = get_api() if not api else api
    api = get_api()
    rtrc = 0
    series = None
    rtlimit = cfg.get('tvdb', 'retry-limit', int)
    rtinterval = cfg.get('tvdb', 'retry-interval', int)    

    while True:
        try:
            series = api[series_name]
        except tvdb_error as e:
            #probably means no connection
            if rtrc >= rtlimit:
                raise
            log.warning(
                'Failed to connect to the tvdb. Retrying in %s seconds.',
                rtlimit
                )            
            time.sleep(rtlimit)
        except tvdb_shownotfound as e:
            log.info(
                'Series \'%s\' was not found on tvdb, falling back on bing/imdb search',
                series_name
                )
            series = bing_lookup(series_name)
            break
            #raise ShowNotFoundError(series_name)
            #raise ShowNotFoundError(series_name), None, sys.exc_info()[2]
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
    series = get_series(ep.clean_name(ep['series_name']))
    log.info('Looking up series: %s', series)
    webep = None
    try:
        webep = series[ep['season_num']][ep['ep_num']]
    except tvdb_seasonnotfound as e:
        raise SeasonNotFoundError(
            series['seriesname'], ep['season_num']), None, sys.exc_info()[2]
    except tvdb_episodenotfound as e:
        raise EpisodeNotFoundError(
            series['seriesname'], ep['season_num'], ep['ep_num']), None, sys.exc_info()[2]
    else:
        return webep
    
    
    
