#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A portal to the tv database.
"""
import sqlite3, logging, os
from datetime import date
import re
from collections import OrderedDict

from . import tvregexes, util
from .util import normpath, split_root_dir, ensure_utf8, ancestry, posixpath
from . import appconfig as cfg
from .texceptions import InitExistingDatabaseError, IncompleteEpisodeError, InvalidArgumentError
from . import __pkgname__


log = logging.getLogger(__pkgname__)

class Episode(OrderedDict):

    """
    Keys mapping to database fields:
    --------------------------
    'id' : the episode's id (from thetvdb) (int)
    'created_at' : the time which episode is added to database (datetime)
    'modified_at' : last modified time of episode in database (datetime)
    'title' : title of episode (str)
    'ep_number' : number of episode in season (int)
    'extra_ep_number' : number of extra episode in file (if any) (int)
    'ep_summary' : plot summary of episode (str)
    'air_date' : date when episode first aired (date)
    'file_path' : path to media file containing episode (relative to source dir) (str)
    'season_id' : id of episode's season (from thetvdb) (int)
    'season_number' : number of season (int)
    'series_id' : id of episode's series (from thetvdb) (int)
    'series_title' : title of series (str)
    'series_summary' : plot summary of series (str)
    'series_start_date' : when series first aired (date)
    'run_time_minutes' : (int)
    'network' : (str)

    keys extracted by the filename parser (not in database):
    ---------------------------
    'release_group' : scene release group
    'which_regex' : which regex matched the episode
    'extra_info' : any seemingly irrelevant text from filename

    This is a dict derived type which does not allow creation of new keys 
    except those listed.
    __setitem__ will convert given values to their correct types 
    when possible.    
    """
    preset_keys = (
        'id',
        'created_at',
        'modified_at',
        'title',
        'ep_number',
        'extra_ep_number',
        'ep_summary',
        'air_date',
        'file_path',
        'season_id',
        'season_number',
        'series_id',
        'series_title',
        'series_summary',
        'series_start_date',
        'run_time_minutes',
        'network',
        #parser keys
        'release_group',
        'which_regex',
        'extra_info',
        )
    numeric_keys = (
        'id',
        'ep_number',
        'extra_ep_number',
        'season_id',
        'season_number',
        'series_id',
        'run_time_minutes'
        )    
    #keys which matter only in local context
    local_keys = (
        'file_path',
        'release_group',
        'extra_ep_number',
        'which_regex',
        'extra_info'
        )

    db_keys = (
        'id',
        'title',
        'ep_number',
        'extra_ep_number',
        'ep_summary',
        'air_date',
        'file_path',
        'season_id',
        'season_number',
        'series_id',
        'series_title',
        'series_summary',
        'series_start_date',
        'run_time_minutes',
        'network'
        )
    
    def __init__(self, path, root_dir):
        #path = util.ensure_utf8(path)
        super(Episode, self).__init__()
        for key in self.preset_keys:
            super(Episode, self).__setitem__(
                key, None
                )
        self['file_path'] = path        
        self.root_dir = normpath(root_dir)

    def safe_update(self, otherep):
        """
        safe_update(dict) -> None\n
        otherep can be an Episode object or any dict like
        object with the same keys.\n
        Unlike dict.update(), this will only update
        'None' values in the destination dict.        
        """
        for key in otherep.keys():
            if self[key] is not None: continue
            self[key] = otherep[key]
            
    def is_fully_parsed(self):
        """
        Ep is fully parsed, true or false.\n
        Will throw key exceptions if self is not a good ep dict.    
        """
        return self['series_title'] and self['season_number'] is not None and self['ep_number'] is not None

    def clean_name(self, name):
        #TODO: find junk
        """
        Strips all kinds of junk from a name.
        """
        junk = tvregexes.junk
        if name is None: return None
        name = re.sub(junk, ' ', name)
        name = name.strip()
        name = name.title()
        return name

    def path(self, form='abs'):
        """
        Return this episode's file path.
        `form` may be 'abs' or 'rel' (absolute or relative)         
        Can also be 'db' which is same as 'rel' but backslashes 
        are always replaced by forward slashes.
        path will be returned in respective form.        
        Relative means relative to `root_dir`.
        """
        if form == 'abs':
            root, path = split_root_dir(self['file_path'], self.root_dir)
            return normpath(os.path.join(root, path))
        elif form == 'rel':       
            return split_root_dir(self['file_path'], self.root_dir)[1]
        elif form == 'db':
            p = split_root_dir(self['file_path'], self.root_dir)[1]
            return posixpath(p)
        else:
            raise InvalidArgumentError(
                'arg `form` must be "abs" or "rel", you gave %s' % form
                )

    def pretty(self):
        """
        Get pretty print output of this episode.
        """
        return '\n'.join(['%s : %s' % (k, v) for k, v in self.iteritems()])
        
    def __setitem__(self, key, value):
        """
        Introducing some type safety and stuff to this dict.\n
        Will implicitly convert any value put in 
        a key in numerics to int.\n
        """
        if key not in self.preset_keys:
            raise KeyError(
                '''\'%s\' is not a valid key for a Episode.
                \nValid keys are: %s''' % (key, self.preset_keys))
        def set_val(val):
            #really set the value to key
            super(Episode, self).__setitem__(key, val)

        if key in self.numeric_keys and value is not None:
            #will raise an error if value is not a valid number
            return set_val(int(value))
        #strings
        if isinstance(value, basestring):
            if value == '' or value is None:
                return set_val(None)
            return set_val(util.ensure_utf8(value))
        return set_val(value)

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
        self.directory = normpath(util.ensure_utf8(directory))
        dbfile = os.path.join(
            directory,
            cfg.get('database', 'local-database-filename')
            )
        super(TVDatabase, self).__init__(dbfile)

    def create_database(self, force=False, soft=False):
        """
        Import the database schema to a new database.
        This will raise a InitExistingDatabaseError if db already exists.
        If force==True: delete existing dbfile before creating.
        If force==True: ignore InitExistingDatabaseError
        """
        if self.db_file_exists():
            if force:
                os.unlink(self.dbfile)
            elif soft:
                return
            else:
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
        log.debug(
            'Will check if id:%s (type:%s) exists in db',
            id_, type(id_)
            )            
        q = 'SELECT * FROM episode WHERE id = ?;'
        res = self.execute_query(q, (id_,), fetch=1)
        if res: return True
        else: return False

    def episode_exists(self, ep):
        """
        episode_exists(Episode) -> bool
        Check if an episode with same id as given already 
        exists in database.
        """
        if not ep['id']:
            #TODO: HACK
            return False 
        return self._exists(ep['id'])        

    def path_exists(self, path):
        """
        path_exists(path) -> bool
        Check whether an episode with given path exists in db.
        Returns True or False respectively.
        """
        """
        path = os.path.relpath(
            os.path.abspath(path), 
            self.directory
            )
        """
        q = 'SELECT id FROM episode WHERE file_path = ?;'
        log.debug(path)
        
        params = (posixpath(ensure_utf8(path)),)
        res = self.execute_query(q, params, fetch=1)
        if res: return True
        else: return False

    def get_episodes(self, where_statement='', params=()):
        """
        get_episode(where_statement='', params=()) -> yield Episode
        yield all episodes matching given where_statement.
        where_statement should be a valid sqlite3 in form 'WHERE [expression]'
        parametarized queries are preferred for safety, but not enforced here.

        If no where_statement is given, all episodes are selected.        
        """
        q = 'SELECT * FROM episode ' + where_statement        
        for row in self.execute_query(q, params):
            e = Episode('', self.directory)
            e.update(row)
            yield e           
    
    def delete_episode(self, epid):
        """
        Delete episode with given `epid` from database.
        """        
        q = 'DELETE FROM episode WHERE id = ?;'
        p = (epid,)
        self.execute_query(q, p, fetch=0)
        

    def _insert_episode(self, epobj):
        q = 'INSERT INTO episode (%s) VALUES (%s);'
        insfields = ','.join(epobj.db_keys)
        insvals = ','.join('?' for x in epobj.db_keys)
        q = q % (insfields, insvals)
        params = [epobj[k] for k in epobj.db_keys]
        self.execute_query(q, params, fetch=0)
        return epobj['id']            

    def _update_episode(self, epobj):
        q = 'UPDATE episode SET %s WHERE id = ?;'
        updfields = ','.join(['%s=?' % (key) for key in epobj.db_keys])
        q = q % updfields
        params = [epobj[k] for k in epobj.db_keys]+[epobj['id']] #add 'id' for the where stmnt
        log.debug('%s\n%s', q, params)
        self.execute_query(q, params, fetch=0)
        return epobj['id']            

    def upsert_episode(self, epobj):
        """
        upsert_episode(LocalEpisode) -> int episode id
        database upsert function.
        Implicitly converts episode's file_path 
        to its relative path from self.directory
        """        
        if not epobj['id']:
            raise IncompleteEpisodeError(
                'Unable to add id-less episode to the database: %s' % epobj
                )  
        epobj['file_path'] = ensure_utf8(epobj.path('db'))
        if self._exists(epobj['id']):
            return self._update_episode(epobj)
        else:
            return self._insert_episode(epobj)

    def add_unparsed_child(self, child_path):
        """
        Will automatically determine the parent path based on child path.
        """
        log.debug('adding unparsed child: %s', child_path)
        root, path = split_root_dir(child_path, self.directory)
        q = '''
            INSERT INTO unparsed_episode(
            child_path, parent_path) VALUES (?, ?);
            '''        
        def do_query(ps):            
            try:
                self.execute_query(
                    q, 
                    (ensure_utf8(ps[0]), ensure_utf8(ps[1])),
                    fetch=0
                    )
            except sqlite3.IntegrityError as e:
                #probable means child_path is not unique
                log.debug(
                    'Error while adding unparsed child '\
                    +'(usually nothing to worry about): %s\nmessage: %s',
                    ps, e.message
                    )
                pass            
        ancest = ancestry(path)
        if not ancest: #no parents
            params = (path, None)
            do_query(params)
        elif len(ancest) == 1: #only parent, no gramps
            params = (path, ancest[0])
            do_query(params)
        else: #grandparents and shit
            do_query((path, ancest[-1])) #put filename itself
            for index, p in enumerate(ancest):
                if index == 0:
                    params = (p, None)
                else:
                    params = (p, ancest[index-1]) #parent is p from before
                do_query(params)        

            

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

