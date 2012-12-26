#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sqlite3
from datetime import datetime

import tvdb_api

import tvunfucker

from . import dirscanner, parser, tvdbwrapper, localdbapi, util
from . import appconfig as cfg
from .texceptions import *
import dbguy

osp = os.path


log = tvunfucker.log
api = tvdbwrapper.get_api()

def create_database(directory, force=False):
    """
    Creates a new, empty database in given |directory| if it does 
    not already exist.
    If force==True, the existing database will be deleted and a new one created instead.

    Raises DatabaseAlreadyExistsError if database exists and |force==False|

    Returns EpisodeSource instance
    """
    dbfile = osp.join(directory, cfg.get('database', 'local-database-filename'))
    if osp.exists(dbfile):
        if force:
            try:
                delete_database(directory)
            except NoSuchDatabaseError:
                pass #don't care
        else:
            raise DatabaseAlreadyExistsError(dbfile)
    source = EpisodeSource(directory)
    source.initialize_database()
    return source


def get_database(directory):
    """
    Returns an EpisodeSource for an existing 
    database in given directory.
    """
    dbfile = osp.join(directory, cfg.get('database', 'local-database-filename'))
    if not osp.exists(dbfile):
        raise NoSuchDatabaseError
    return EpisodeSource(directory)

def scrape_source(source):
    """
    Scan the given EpisodeSource instance for tv shows.    
    Creates a new sqlite tv database in the given source_dir.\n
    If kwarg |create| is False, only an existing database source will be returned.
    """
    unparsed = []
    try:
        source = create_database(source.source_dir)
    except DatabaseAlreadyExistsError:
        pass
    for ep in get_parsed_episodes(source.source_dir):
        webep = None
        #print ep['path']
        try:
            log.info('looking up file at %s', ep['path'])
            webep = None
            webep = tvdbwrapper.lookup(ep)
            #TODO: catch the right exceptions
        except (ShowNotFoundError, SeasonNotFoundError, EpisodeNotFoundError) as e:
            #raise
            log.error(e.message)
            log.debug('unparsed episode')
            ep['path'] = os.path.relpath(ep['path'], source.source_dir)
            source.add_unparsed_child(ep['path'])
            unparsed.append(ep)
        else:
            log.debug(ep)
            ep['tvdb_ep'] = webep
            #TODO: ugly hack, tackle this when eps are spawned
            ep['path'] = os.path.relpath(ep['path'], source.source_dir)
            source[ep['path']] = ep
            log.info('Adding episode at: %s', ep['path'])
            if webep:
                log.debug('adding ep to db %s', ep)
                try:
                    source.add_episode_to_db(ep)
                except sqlite3.IntegrityError:
                    log.error(
                        'episode already exists in db: %s. Ignoring.',
                        ep['path']
                        )
            else: 
                log.info('Ep is going to unparsed: %s', ep['path'])                
                source.add_unparsed_child(ep['path'])
                unparsed.append(ep)
                

    log.info('Failed to scrape %s episodes', len(unparsed))
    log.debug('\n'.join([e['path'] for e in unparsed])) #TODO: Exception here, expects string
    return source

def delete_database(source_dir):
    """
    Deletes the tvunfucker database file from given directory.
    """
    dbfile = os.path.join(
        source_dir, cfg.get(
        'database', 
        'local-database-filename')
        )
    try:
        os.unlink(dbfile)
    except OSError as e:
        if e.errno == 2: #file no exist
            raise NoSuchDatabaseError(dbfile), None, sys.exc_info()[2]
        else: raise


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


#TODO: Move this somewhere more appropriate
class EpisodeSource(dict):
    """
    Holds together a whole tv source.\n
    This would represent a single tv directory and database.
    """
    def __init__(self, sourcedir):
        self.source_dir = sourcedir
        super(EpisodeSource, self).__init__()
        self.db_file = os.path.join(
            self.source_dir, cfg.get('database','local-database-filename')
            )
        self.db = localdbapi.Database(self.db_file)

    def initialize_database(self):
        #TODO: name doesn't describe this, maybe create_database?
        """
        Use when you want to create a new database.
        """
        log.debug(
            'going to import schema into db file at: %s',
            self.db_file
            )
        schema = open(
            os.path.join(
                os.path.dirname(tvunfucker.__file__), 'schema.sql')
                ).read()
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.executescript(schema)
        conn.commit()
        conn.close()

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

    def get_unparsed_children(self, parent_path):
        op = 'is' if parent_path is None else '='
        where = localdbapi.make_where_statement(operator=op, parent_path=parent_path)
        return self.db.get_rows(
            'SELECT * FROM unparsed_episode '+where[0],
            params=where[1]
            )

    def get_unparsed_entity(self, child_path):
        where = localdbapi.make_where_statement(child_path=child_path)
        return self.db.get_rows(
            'SELECT * FROM unparsed_episode '+where[0],
            params=where[1]
            )
    
    def add_unparsed_child(self, child_path):
        """
        Will automatically determine the parent path based on child path.
        """
        log.debug('adding unparsed child: %s', child_path)
        while True:
            q = '''
            INSERT INTO unparsed_episode (
            child_path, parent_path, filename) 
            VALUES (?, ?, ?);
            '''
            splitted = os.path.split(child_path)            
            parent = None if not splitted[0] else splitted[0]
            filename = util.split_path(child_path).pop()
            params = (child_path, parent, filename)
            try:
                self.db.insert(q, params)
            except sqlite3.IntegrityError as e:
                #probable means child_path is not unique, should probly check for that
                log.warning(
                    'Error while adding unparsed child (usually nothing to worry about): %s\nmessage: %s',
                    child_path, e.message
                    )
                pass
            #new path
            if parent == None: break            
            child_path = parent

    def add_episode_to_db(self, ep):
        """
        add_episode_to_db(parser.Episode)
        """
        util.type_safe(
            ep, dbguy.Episode,
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

        self.db.insert(q, params)        

    def add_season_to_db(self, ep):
        """
        add_season_to_db(parser.Episode)
        """
        util.type_safe(
            ep, dbguy.Episode,
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

        self.db.insert(q, params)

        #TODO: upsert if season exists

    def add_series_to_db(self, ep):
        """
        add_series_to_db(parser.Episode)
        """
        util.type_safe(
            ep,
            dbguy.Episode,
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
            self.db.insert(query, params)
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
        result = self.db.get_row(q, (pk,))
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
        

