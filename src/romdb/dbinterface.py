#!/usr/bin/env python
#encoding:utf-8

import sqlite3, os

import dbinterface
from romexception import *
from romlog import *

class TVDBManager(object):

    _queries = { #fuck this shit
        'add_series' :
        '''
        INSERT INTO series (id, title, summary, first_air, run_time, network)
        VALUES (?,?,?,?,?,?)
        ''' ,
        'add_season' :
        '''
        INSERT INTO season (id, season_number, series_id)
        VALUES (?, ?, ?);
        ''',
        'add_episode' :
        '''
        INSERT INTO episode (id, episode_number, title, air_date, summary, filename, season_id)
        VALUES (?,?,?,?,?,?,?);
        '''

        }    
    
    def __init__(self, dbfilename, overwrite=False):
        """
        Overwrite will delete the existing database and make new one.
        """
        if os.path.exists(dbfilename) and overwrite:
            os.unlink(dbfilename)
        if not os.path.exists(dbfilename):
            self.create_tv_database(dbfilename)
        self.db = dbfilename

    def create_tv_database(self, filename):
        """
        create_tv_database(filename) -> None
        Creates a new tv database with the given filename.

        """
        schema = open(os.path.join(os.path.dirname(dbinterface.__file__), 'tvdb.sql')).read()
        conn = sqlite3.connect(filename)
        cur = conn.cursor()
        cur.executescript(schema)
        conn.commit()
        conn.close()    

    def run_query(self, query, params=tuple(), get_one=False, get_none=False):
        """
        run_query(query, params) -> []\n
        run_query(query, params,get_one=True) -> object\n
        If get one, returns the first row in the result set.\n
        If get_none, it will return the last row id
        """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(query, params)
        ret = None
        if get_one: ret = cur.fetchone()
        elif get_none: ret = cur.lastrowid
        else: ret = cur.fetchall()
        conn.commit()
        conn.close()
        return ret

    def item_exists(self, item_type, id_):
        """
        item_exists(str/unicode, integer id) -> int or False\n
        Check if item of given type and id exists.\n
        Allowed types are series, season and episode.\n
        Returns the id if item exists, otherwise False.
        """
        supported = ('series, season, episode')
        if not item_type in supported:
            raise InvalidArgumentError(
                '\'%s\' is not a valid item_type.\n'
                +'item_type must be one of %s.' % (item_type, supported)
                )
        query = 'SELECT id FROM %s WHERE id = ?;' % item_type
        iid = self.run_query(query, (id_,), get_one=True)
        if not iid: return False
        return iid[0]
        

    def _add_series(self, series):
        """
        _add_series(tvdb_api.Series) -> int series id\n
        Checks if the series exists first, if not it adds it.
        """
        d = series.data       
        sid = int(d['id'])

        if self.item_exists('series', sid):
            return sid
        
        #series no exists, add it
        sid = self.run_query(
            self._queries['add_series'],
            params=(
                sid, d['seriesname'], d['overview'],
                d['firstaired'], d['runtime'], d['network']
                ),
            get_none=True
            )
        return sid

    def _add_season(self, episode):
        """
        _add_season(tvparser.Episode) -> int season id\n
        """
        tep = episode.tvdb_ep
        seasid = int(tep['seasonid'])
        if self.item_exists('season', seasid):
            return seasid

        #season no exists, add it
        seasid = self.run_query(
            self._queries['add_season'],
            params=(seasid,int(tep['seasonnumber']),int(tep['seriesid'])),
            get_none=True
            )
        return seasid
                
    
    def add_episode(self, episode):
        """
        add_episode(tvparser.Episode) -> integer episode id
        """
        tepisode = episode.tvdb_ep
        series_id = self._add_series(tepisode.season.show)
        season_id = self._add_season(episode)
        ep_id = int(tepisode['id'])
        if self.item_exists('episode', ep_id):
            rom_log.debug('Episode with id \'%s\' already exists' % ep_id)
            prevep = self.run_query(
                'SELECT id,title,filename FROM episode WHERE id = ?', (ep_id,)
                )
            rom_log.debug('Existing ep data [%s]' %prevep)
            rom_log
            return ep_id
        params=(
            ep_id,
            episode['ep_num'],
            tepisode['episodename'],
            tepisode['firstaired'],
            tepisode['overview'],
            episode.path,
            season_id
            )        
        ep_id = self.run_query(
            self._queries['add_episode'],
            params=params,
            get_none=True                    
            )
        return ep_id

#TODO: TEST EVERYTHING
    

def test():
    #create_tv_database('/home/steini/.testage/testtvdb.sqlite')
    pass
    


def main():
    test()

if __name__ == '__main__':
    main()


