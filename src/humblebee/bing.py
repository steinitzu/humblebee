#!/usr/bin/env/python
#encoding:utf-8

"""
A simple web search interface to the bing search api.
"""
import tempfile, os, getpass, base64, re
from urllib import quote
from json import JSONDecoder
from md5 import new as _md5

import httplib2

def _dir_exists(path):
    return os.path.exists(path) and os.path.isdir(path)

def _get_cache_dir():
    return os.path.join(
        tempfile.gettempdir(), 'bingpy-'+getpass.getuser()
        )

re_url_scheme    = re.compile(r'^\w+://')
re_slash         = re.compile(r'[?/:|]+')
def _safecachename(filename):
    """Return a filename suitable for the cache.

    Strips dangerous and common characters to create a filename we
    can use to store the cache in.
    """

    try:
        if re_url_scheme.match(filename):
            if isinstance(filename,str):
                filename = filename.decode('utf-8')
                filename = filename.encode('idna')
            else:
                filename = filename.encode('idna')
    except UnicodeError:
        pass
    if isinstance(filename,unicode):
        filename=filename.encode('utf-8')
    filemd5 = _md5(filename).hexdigest()
    filename = re_url_scheme.sub("", filename)
    filename = re_slash.sub(",", filename)

    # limit length of filename
    if len(filename)>80:
        filename=filename[:80]
    return ",".join((filename, filemd5))
    

class Bing(object):

    search_url = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%%27web%%27&Query=%%27%(query)s%%27&$format=json'

    def __init__(self, api_key=None, caching=True, cache_dir=None, headers={}):
        """
        Bing(api_key=None, caching=True, cache_dir=None)
        Make a new instance of the Bing api with given api_key
        if caching==True requests will be cached.
        If cache_dir is provided as well, it will be used to store the cache, 
        otherwise it will stored in the system's temp directory.
        given cache_dir must exist, otherwise an OSException will be raised.

        Additionally you can pass http request headers in headers dict in
        the form of 'header':'value' (e.g. 'cache-control':'max-age=9000').
        These headers will be passed for every bing request.
        """
        self.api_key = api_key
        self.caching = caching
        if caching:
            self.cache = self._get_file_cache(cache_dir)        
        else:
            self.cache = None
        self.headers = headers
        self.http = self.get_http()

    def get_http(self):
        h = httplib2.Http(cache=self.cache)
        return h        

    def get_json(self, query):
        """
        Returns the raw JSON for given query.
        """
        url = self.search_url % {'query' : quote(query.encode('utf-8'))}
        bsixfour = base64.encodestring(
            '%s:%s' % (self.api_key, self.api_key)
            ).replace('\n', '')                
        #TODO: cache control header should be configable
        headers = {'Authorization' : 'Basic %s' % bsixfour}
        headers.update(self.headers)
        resp = self.http.request(url, headers=headers)
        return resp[1]

    def get_results(self, query):
        """
        Returns a list of web results as dicts.
        """
        json = self.get_json(query)
        return JSONDecoder().decode(json)['d']['results'][0]['Web']

    
    def __getitem__(self, query):
        return self.get_results(query)

    def _get_file_cache(self, cache_dir):
        cache_dir = cache_dir or _get_cache_dir()
        fc = httplib2.FileCache(
            cache_dir,
            safe=_safecachename
            )
        return fc
            



    
            
            
