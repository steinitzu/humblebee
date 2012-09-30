#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3, logging

import logger

#TODO: separate dbapi from EpisodeSource and put it here

log = logging.getLogger('tvunfucker')
sqlite3.enable_shared_cache(True)

"""
Connection pool make sense with sqlite/
Create a test database with all the test tv
"""
class Database(object):

    def __init__(self, dbfile):
        self.db_file = dbfile
        self.conn = self.db_to_ram()

    @logger.log_time
    def get_connection(self):
        """
        Returns a connection to the sqlite database.
        """
        return self.conn
        """
        conn = sqlite3.connect(self.db_file, detect_types=True)
        conn.row_factory = sqlite3.Row
        return conn
        """

    def db_to_ram(self):
        memdb = sqlite3.connect(':memory:', detect_types=True)
        memdb.row_factory = sqlite3.Row        
        disk = sqlite3.connect(self.db_file, detect_types=True)

        a = ''
        for line in disk.iterdump():
            log.debug(line)
            a+=line

        memdb.executescript(q)
        return memdb

    @logger.log_time
    def _get_row(self, query, params=(), oneormany='one'):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        #TODO: error handling, conn doesn't close if error        
        if oneormany == 'one':
            result = cur.fetchone()
        elif oneormany == 'many':
            result = cur.fetchall()
        else:
            raise ValueError(
                'last argument must be either "one" or "many"'
                )
        conn.close()
        return result

    def get_row(self, query, params=()):
        #TODO: make it take params too
        
        return self._get_row(query, params, 'one')

    def get_rows(self, query, params=()):
        log.debug('query: %s', query)
        log.debug('params: %s', params)        
        return self._get_row(query, params, 'many')

def make_where_statement(dicta=None, operator='=', separator='AND', **kwargs):
    """
    make_where_statement(operator='=', separator='AND', **kwargs) -> ('', (,))
    Makes a simple where statement, compatible with get_rows and get_row.\n
    Default operator used between col and value is '=' (equals)\n
    Available operators include everything supported by the dbms\n
    e.g. '>', '<', '!=', 'LIKE' (text fields), 'ILIKE', etcetera\n\n
    separator can be 'AND', 'OR' or anything else the dbms supports.

    Takes any other named arg and intperpres as a column name:value pair.    
    """
    dicta=dicta if dicta else kwargs
    if not dicta:
        return ('', ())
    sufstring = ''
    sufparams = []
    for key, value in dicta.iteritems():
        pref = 'WHERE' if not sufstring else separator
        sufstring += '%s %s %s ? ' % (pref, key, operator)
        sufparams.append(value)

    return (sufstring, sufparams)                
