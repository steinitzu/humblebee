#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3, logging
from threading import Lock

import logger, cfg
from texceptions import PoolExhaustedError, PutUnkeyedConnectionError

#TODO: separate dbapi from EpisodeSource and put it here

log = logging.getLogger('tvunfucker')


class ThreadPool(object):
    def __init__(self, minconn, maxconn, dbfile):        
        self._used = {}
        self._rused = {}
        self._pool = []
        self.minconn = minconn
        self.maxconn = maxconn
        self.dbfile = dbfile
        self._lock = Lock()

    def _connect(self, to_pool=True):
        """
        Open a new connection and add it to the pool if to_pool==True.
        """
        conn = sqlite3.connect(self.dbfile, detect_types=True)
        conn.row_factory = sqlite3.Row
        if to_pool:
            self._pool.append(conn)
        return conn

    def _get_conn(self, key=None):
        if key is not None and key in self._used:
            return self._used[key]
        try:
            conn = self._pool.pop()
        except IndexError:
            log.debug('Pool is empty, making new connection')
            if len(self._used) == self.maxconn:
                raise PoolExhaustedError()            
            conn = self._connect(to_pool=False)
        if key is None: 
            #two connections could have the same key, 
            #but never at the same time, dno if problem
            key = id(conn)
        self._used[key] = conn
        self._rused[id(conn)] = key
        return conn                        

    def get_conn(self, key=None):
        """
        Get a free connection from pool and 
        assign a key to it (key is id(conn) if key==None).
        """
        self._lock.acquire()        
        try:
            return self._get_conn(key)
        finally:
            self._lock.release()

    def _put_conn(self, conn, key=None, close=False):
        if key is None: key = self._rused.get(id(conn))
        if key is None:
            raise PutUnkeyedConnectionError()

        if close:
            conn.close()
        else:
            #rollback transactions before putting back to pool
            try:
                conn.rollback()
            except sqlite3.ProgrammingError as e:
                #this usually means conn is closed
                log.warning(
                    'ProgrammingError when rolling '\
                    +'back transaction suppressed\n'\
                    +'Message: %s', e.message
                    )
                close = True

        del self._used[key]
        del self._rused[id(conn)]
        if not close and (len(self._pool) < self.minconn or len(self._pool) < self.maxconn):
            self._pool.append(conn)

    def put_conn(self, conn, key=None, close=False):
        """
        Put the connection back.
        """
        self._lock.acquire()
        try:
            self._put_conn(conn, key, close)
        finally:
            self._lock.release()        


class Database(object):

    def __init__(self, dbfile):
        self.db_file = dbfile
        self.pool = ThreadPool(
            cfg.get('database', 'pool-minconn'),            
            cfg.get('database', 'pool-maxconn'),
            dbfile
            )
        #self.conn = self.db_to_ram()

    @logger.log_time
    def get_connection(self):
        """
        Returns a connection to the sqlite database.
        """
        #return self.conn
        return self.pool._connect(to_pool=False)
        
    @logger.log_time
    def _get_row(self, query, params=(), oneormany='one'):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params)
            #TODO: error handling, conn doesn't close if error        
            if oneormany == 'one':
                result = cur.fetchone()
            elif oneormany == 'many':
                result = cur.fetchall()
            elif oneormany == 'none':
                result = None
            else:
                raise ValueError(
                    'last argument must be either "one" or "many"'
                    )
            conn.commit()
        finally: conn.close()
            #self.pool.put_conn(conn)
        return result

    def get_row(self, query, params=()):
        return self._get_row(query, params, 'one')

    def get_rows(self, query, params=()):
        log.debug('query: %s', query)
        log.debug('params: %s', params)        
        return self._get_row(query, params, 'many')

    def insert(self, query, params=()):
        log.debug('query: %s', query)
        log.debug('params: %s', params)                
        return self._get_row(query, params, oneormany='none')

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
