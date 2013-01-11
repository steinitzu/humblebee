#!/usr/bin/env python
# -*- coding: utf-8 -*-

#builtin
import time, logging, sys, re
from datetime import datetime

#3dparty
from .tvdb_api.tvdb_api import tvdb_error, Tvdb, tvdb_shownotfound, tvdb_seasonnotfound, tvdb_episodenotfound

#this pkg
from .texceptions import ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError
from .texceptions import NoIdInURLError, IncompleteEpisodeError
from . import __pkgname__
from . import appconfig as cfg
from .bing import Bing
from .dbguy import Episode
from .util import string_dist

log = logging.getLogger(__pkgname__)

#tiss a ssingleton
_api = None
_bing_api = None

def get_api():
    #THERE Can be only one.... api
    global _api
    if not _api:
        _api = Tvdb(apikey=cfg.get('tvdb', 'api-key'), actors=True)
    return _api

def get_bing_api():
    global _bing_api
    if not _bing_api:
        _bing_api = Bing(
            api_key=cfg.get('bing', 'api-key'), 
            caching=True,
            headers={'cache-control':'max-age=%s' % cfg.get('bing', 'cache-max-age')}
            )
    return _bing_api

def _imdb_id_from_url(url):
    """
    Parse the imdb id from an url like 'imdb.com/title/tt0092455'.
    """
    log.debug('URL: %s', url)
    m = re.search(r'title/(?P<id>tt\d{7})', url)  
    if not m:
        raise NoIdInURLError('No imdb id in url: %s' % url)
    return m.groupdict()['id']

def get_imdb_id(series_name):
    """
    get_imdb_id(series_name) -> str imdb_id
    Get matching imdb id for given series name using bing search.
    """
    query = 'site:imdb.com %s "TV Series"' % series_name
    bing = get_bing_api()
    searchres = bing[query]
    if not searchres:
        raise ShowNotFoundError(
            'Search query returned zero results for series name: "%s"' % (
                series_name)
            )
    try: #parse id out of first result
        imdbid = _imdb_id_from_url(searchres[0]['Url'])
    except NoIdInURLError as e:
        raise ShowNotFoundError(
            'Unable to accurately get an imdb id for series name: "%s"' % (
                series_name)
            )
    return imdbid

def _get_series(series_name, imdb_id=None):
    """
    _get_series(series_name, imdb_id=None) -> tvdb_api.Show
    """
    tvdb = get_api()
    try:
        if imdb_id:
            return tvdb[imdb_id, 'imdb']
        else:
            return tvdb[series_name]
    except tvdb_shownotfound as e:
        raise ShowNotFoundError(e.message)

def get_series(series_name):
    """
    get_series(str series_name) -> tvdb_api.Show
    """
    try:
        imdbid = get_imdb_id(series_name)
        log.debug('Got imdb id "%s" (series_name: "%s").', imdbid, series_name)
    except ShowNotFoundError as e:
        log.warning(e.message)
        imdbid = None

    rtlimit = cfg.get('tvdb', 'retry-limit', int)
    rtinterval = cfg.get('tvdb', 'retry-interval', int)    
    rtcount = -1
    series = None    
    while True:
        rtcount+=1
        try:
            series = _get_series(series_name, imdbid)
        except ShowNotFoundError as e:
            if imdbid: 
                rtcount-=1
                imdbid = None #try again with name lookup
                continue
            else:
                raise
        except tvdb_error as e:
            if rtcount >= rtlimit:
                raise
            rtcount+=1
            log.warning(
                'Failed to connect to the tvdb. Retrying in %s seconds. '\
                +'On retry attempt no. %s\nmessage: %s',
                rtlimit, rtcount, e.message
                )            
            time.sleep(rtinterval)
        else:
            break
    def __raiserr():
        raise ShowNotFoundError(
            'No matching series found for "%s"' % series_name
            )
    if series:
        dist = string_dist(series['seriesname'], series_name)
        if dist > 0.9:
            #too far off
            log.debug(
                'Asked for "%s", got "%s". Dist: %s',
                series_name, series['seriesname'], dist
                )
            __raiserr()
        else:
            return series
    else: __raiserr()           

def lookup(ep):
    """
    lookup(Episode) -> Episode with same path as input
    Looks up given episode at tvdb and returns a new one with full info.
    Raises SeasonNotFoundError and EpisodeNotFoundError
    """
    if not ep.is_fully_parsed():
        raise IncompleteEpisodeError(
            'Episode does not have sufficient info for lookup\n%s' % ep
            )
    series = get_series(ep.clean_name(ep['series_title']))
    log.info('Looking up series: %s', series)
    newep = Episode(ep.path(), ep.root_dir)
    #put base info in new ep
    for key in newep.local_keys:
        newep[key] = ep[key]
    webep = None
    try:
        webep = series[ep['season_number']][ep['ep_number']]
    except tvdb_seasonnotfound as e:
        raise SeasonNotFoundError(
            series['seriesname'], ep['season_number']), None, sys.exc_info()[2]
    except tvdb_episodenotfound as e:
        raise EpisodeNotFoundError(
            series['seriesname'], ep['season_number'], ep['ep_number']), None, sys.exc_info()[2]
    else:
        return _update_ep_with_tvdb_ep(newep, webep)

def _safe_string_to_date(dstring):
    """
    tvdb format date '2004-11-12' to python datetime.date
    Returns None in case of failure.
    """
    try:        
        dt = datetime.strptime(dstring, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None
    else:
        return dt.date()

def _update_ep_with_tvdb_ep(ep, webep):
    """
    _update_ep_with_tvdb_ep(ep, webep) -> same ep
    Updates the given ep with info from webep.
    webep is a tvdb_api.Episode in this context.
    """
    show = webep.season.show
    ep['id'] = webep['id']
    ep['title'] = webep['episodename']
    ep['ep_number'] = webep['episodenumber']
    ep['ep_summary'] = webep['overview']
    ep['air_date'] = _safe_string_to_date(webep['firstaired'])
    ep['season_id'] = webep['seasonid']
    ep['season_number'] = webep['seasonnumber']
    ep['series_id'] = webep['seriesid']
    ep['series_title'] = show['seriesname']
    ep['series_summary'] = show['overview']
    ep['series_start_date'] = _safe_string_to_date(
        show['firstaired']
        )
    ep['run_time_minutes'] = show['runtime']
    ep['network'] = show['network']
    return ep
