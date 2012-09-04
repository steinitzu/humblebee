import os, sqlite3
from datetime import datetime

import tvdb_api

import tvunfucker

import dirscanner
import parser
import tvdbwrapper
import config
from texceptions import *
import tutil



log = tvunfucker.log
api = tvdb_api.Tvdb(apikey=tvunfucker.tvdb_key, actors=True)


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
    if not ep.is_fully_parsed():
        return None
    series = tvdbwrapper.get_series(ep.clean_name(ep['series_name']), api)
    if not series:
        return None
    webep = series[ep['season_num']][ep['ep_num']]
    #ep['tvdb_ep'] = webep
    return webep
    #return ep


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

    def run_query(self, query, params, get_one=False, get_none=False):
        """
        run_query(query, params) -> []\n
        run_query(query, params,get_one=True) -> object\n
        If get one, returns the first row in the result set.\n
        If get_none, it will return the last row id
        """        
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute(query, params)
        ret = None
        if get_one: ret = cur.fetchone()
        elif get_none: ret = cur.lastrowid
        else: ret = cur.fetchall()
        conn.commit()
        conn.close()
        return ret

    def add_episode_to_db(self, ep):
        """
        add_episode_to_db(parser.LocalEpisode)
        """
        tutil.type_safe(
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
            datetime.strptime(webep['firstaired'], '%Y-%m-%d').date(),
            ep['path'],
            season_id
            )

        self.run_query(q, params, get_none=True)        

    def add_season_to_db(self, ep):
        """
        add_season_to_db(parser.LocalEpisode)
        """
        tutil.type_safe(
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
        tutil.type_safe(
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
            datetime.strptime(d['firstaired'], '%Y-%m-%d').date(),
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
            log.info(ep)
            source[ep['path']] = ep

    log.info('\n***UNPARSED EPISODES***\n')
    log.info('count: %d\n' % len(unparsed))
    log.info('\n'.join([e for e in unparsed])) #TODO: Exception here, expects string
