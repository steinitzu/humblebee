#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A portal to the tv database.
"""

import sqlite3, logging, os
from datetime import date

from . import cfg
from .texceptions import InitExistingDatabaseError, IncompleteEpisodeError


log = logging.getLogger('tvunfucker')

        

class Database(object):
    """
    Handles database connections and direct query executions.
    """
    def __init__(self, dbfile):
        self.dbfile = dbfile

    def db_file_exists(self):
        """
        Checks if self.dbfile exists.
        Convenience function.
        """
        return os.path.exists(self.dbfile)

    def _get_connection(self):
        conn = sqlite3.connect(self.dbfile, detect_types=True)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query, params=(), fetch=-1, isscript=False):
        """
        Executes the given query with given params.
        optional argument 'fetch' decides how many rows to 
        return from resultset.\n
        fetch==0 -> None
        fetch==1 -> [row]
        fetch<0 -> [all rows,...]
        fetch>1 -> fetchmany(fetch)

        Default is -1 (all rows) (cursor.fetchall)
        rows are returned as a list of |sqlite3.Row| objects.

        If isscript==True it will use cursor.executescript to exec.

        Can raise all kinds of databaseerrors.
        """
        #TODO: wrap errors into some friendly packages.
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            if isscript:
                cur.executescript(query)
            else:
                cur.execute(query, params)                
            if fetch < 0:
                result = cur.fetchall()
            elif fetch == 1:
                result = cur.fetchone()
            elif fetch == 0:
                result = None
            elif fetch > 1:
                result = cur.fetchmany(fetch)
            conn.commit()
        finally:
            conn.close()
        return result

class TVDatabase(Database):
    def __init__(self, directory):
        dbfile = os.path.join(
            directory,
            cfg.get('database', 'local-database-filename')
            )
        super(TVDatabase, self).__init__(dbfile)

    def create_database(self):
        """
        Import the database schema to a new database.
        This will raise a InitExistingDatabaseError if db already exists.
        """
        if self.db_file_exists():
            raise InitExistingDatabaseError(self.dbfile)
        schema = open(
            os.path.join(
                os.path.dirname(__file__), 'schema.sql')).read()
        self.execute_query(schema, isscript=True)

    def _exists(self, id_):
        """
        _exists(id_) -> True or False
        Check if row with given id_ exists in episode table.                
        """
        q = 'SELECT * FROM episode WHERE id = ?;'
        res = self.execute_query(q, (id_,), fetch=1)
        if res: return True
        else: return False

    def upsert_episode(self, epobj):
        """
        upsert_episode(LocalEpisode) -> int episode id
        database upsert function.
        """

        if not epobj['id']:
            raise IncompleteEpisodeError(
                'Unable to add id-less episode to the database: %s' % epobj
                )        
        params = []
        if self._exists(epobj['id']):
            q = 'UPDATE episode SET %s WHERE id = ?;'
            updfields = ','.join(['%s=?' % (key) for key in epobj.iterkeys()])
            q = q % updfields
            params = epobj.values()+[epobj['id']]        
        else:
            q = 'INSERT INTO episode (%s) VALUES (%s);'
            insfields = ','.join(epobj.keys())
            insvals = ','.join(['?' for x in xrange(len(epobj))])
            q = q % (insfields, insvals)
            params = epobj.values()
        self.execute_query(q, params, fetch=0)
        return epobj['id']            
            

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

