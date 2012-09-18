#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sqlite3
from datetime import datetime

import tvdb_api

import tvunfucker

import dirscanner, parser, tvdbwrapper, config, localdbapi, util
from texceptions import *


log = tvunfucker.log
api = tvdbwrapper.get_api()


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
    tvdb_api.Episode object to it's 'tvdb_eop' key.    
    """
    raise DeprecationWarning()
    if not ep.is_fully_parsed():
        return None
    series = tvdbwrapper.get_series(ep.clean_name(ep['series_name']),)
    log.info('series: %s', series)
    if not series:
        return None
    webep = series[ep['season_num']][ep['ep_num']]
    #ep['tvdb_ep'] = webep
    return webep
    #return ep


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
    

#TODO: Move this somewhere more appropriate
class EpisodeSource(dict):
    """
    Holds together a whole tv source.\n
    This would represent a single tv directory.
    """
    def __init__(self, sourcedir):
        self.source_dir = sourcedir
        super(EpisodeSource, self).__init__()
        self.db_file = os.path.join(self.source_dir, config.local_database_filename)
        self.db = localdbapi.Database(self.db_file)

    def initialize_database(self):
        #TODO: name doesn't describe this, maybe create_database?
        """
        Use when you want to create a new database.
        """
        schema = open(os.path.join(os.path.dirname(tvunfucker.__file__), 'schema.sql')).read()
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executescript(schema)
        conn.commit()
        conn.close()

    def run_query(self, query, params=(), get_one=False, get_none=False):
        """
        run_query(query, params) -> []\n
        run_query(query, params,get_one=True) -> object\n
        If get one, returns the first row in the result set.\n
        If get_none, it will return the last row id
        """        
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        log.debug('Query: %s\nParams: %s', query, params)
        ret = None
        try:
            cur.execute(query, params)
            if get_one: ret = cur.fetchone()
            elif get_none: ret = cur.lastrowid
            else: ret = cur.fetchall()
            conn.commit()
        except sqlite3.OperationalError, sqlite3.IntegrityError:
            raise
        finally:
            conn.close()            
        return ret

    def get_series(self, series_id):
        return self.db.get_row(
            'SELECT * FROM view_series WHERE id = ?',
            (int(series_id),)
            )

    def get_season(self, season_id):
        return self.db.get_row(
            'SELECT * FROM view_season WHERE id = ?',
            (int(season_id),)
            )

    def get_episode(self, episode_id):
        return self.db.get_row(
            'SELECT * FROM view_episode WHERE id = ?',
            (int(season_id),)
            )

    def _get_entities(self, e_type, **kwargs):
        """
        _get_entities(column1=value1, column2=value2) -> sqlite3.Row\n
        Accepts a variable number of arguments. This will be the where statement.
        """
        where = localdbapi.make_where_statement(dicta=kwargs)
        e_type = 'view_'+e_type
        return self.db.get_rows(
            'SELECT * FROM %s %s' % (e_type, where[0]),
            params=where[1]
            )        

    def get_series_plural(self, **kwargs):
        """
        Returns all series where column matches value.
        """
        return self._get_entities('series', **kwargs)

    def get_seasons(self, **kwargs):
        #TODO: Do same thing with get_seriess and episodes
        """
        Takes column=value kwargs
        """
        return self._get_entities('season', **kwargs)

    def get_episodes(self, **kwargs):
        """
        Returns all episode where column matches value.\n
        Takes named args like _get_entities.
        """
        return self._get_entities('episode', **kwargs)

    def add_episode_to_db(self, ep):
        """
        add_episode_to_db(parser.LocalEpisode)
        """
        util.type_safe(
            ep, parser.LocalEpisode,
            arg_num=1
            )
        webep = ep['tvdb_ep']
        log.debug(webep.keys())
        season_id = int(webep['seasonid'])
        if not self.season_exists(season_id):
            self.add_season_to_db(ep)

        q = '''
            INSERT INTO episode (
                id,
                ep_number,
                extra_ep_number,
                title,
                summary,
                air_date,
                file_path,
                season_id
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            '''
        exep = None
        if ep['extra_ep_num'] is not None:
            exep = int(ep['extra_ep_num'])
        params = (
            int(webep['id']),
            int(webep['episodenumber']),
            exep,
            webep['episodename'],
            webep['overview'],
            util.safe_strpdate(webep['firstaired']),
            ep['path'],
            season_id
            )

        self.run_query(q, params, get_none=True)        

    def add_season_to_db(self, ep):
        """
        add_season_to_db(parser.LocalEpisode)
        """
        util.type_safe(
            ep, parser.LocalEpisode,
            arg_num=1
            )
        webep = ep['tvdb_ep']
        show_id = int(webep.season.show['id'])
        if not self.series_exists(show_id):
            self.add_series_to_db(ep)

        q = 'INSERT INTO season (id, season_number, series_id) VALUES (?, ?, ?);'
        params = (
            int(webep['seasonid']),
            int(webep['seasonnumber']),
            show_id
            )

        self.run_query(q, params, get_none=True)

        #TODO: upsert if season exists

    def add_series_to_db(self, ep):
        """
        add_series_to_db(parser.LocalEpisode)
        """
        util.type_safe(
            ep,
            parser.LocalEpisode,
            arg_num=1
            )
        if not ep['tvdb_ep']:
            raise IncompleteEpisodeError(
                'The given episode does not contain a valid tvdb episode.\n%s' %
                ep
                )
        ep = ep['tvdb_ep']

        season = ep.season
        series = season.show
        query = '''
            INSERT INTO series (id, title, summary, start_date, run_time_minutes, network)
            VALUES (?, ?, ?, ?, ?, ?);
            '''
        d = series.data
        #tvdb_api episode stores everything in strings, need to cast shit
        params = (
            int(d['id']),
            d['seriesname'],
            d['overview'],
            util.safe_strpdate(d['firstaired']),
            int(d['runtime']),
            d['network']
            )
        try:
            self.run_query(query, params)
        except sqlite3.IntegrityError:
            #this usually means the series with this id already exists.
            #we should make a column with 'lastupdate' (tvdb ep has that too)
            #check that and if it's newer, we update the data here
            #--- much later, High self, says "that makes sense" (upsert)
            raise

    def _item_exists(self, pk, item_type):
        """
        _item_exists(self, int id, item_type 'season'||'series'||episode)
        -> bool
        """
        pk = int(pk)
        item_type = 'view_'+item_type
        q = 'SELECT id FROM %s WHERE id = ?;' % item_type
        result = self.run_query(q, (pk,), get_one=True)
        if result: return True
        return False        
        
    def season_exists(self, season_id):
        return self._item_exists(season_id, 'season')        

    def series_exists(self, series_id):
        """
        series_exists(int) -> bool\n
        Returns True or False depending on wheather
        the given series_id exists in the database.
        """
        return self._item_exists(series_id, 'series')
        

