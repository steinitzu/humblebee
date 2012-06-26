import time

import tvdb_api

import config

def get_series(series_name, api):
    retrycount = 0
    series = None
    while True:
        try:
            series = api[series_name]
            break
        except tvdb_api.tvdb_shownotfound as e:
            break
        except tvdb_api.tvdb_error as e:
            #probably couldn't connect
            if retrycount >= config.tvdb_retry_limit:
                raise #no way hose
            time.sleep(config.tvdb_retry_interval)
        else:
            break
    return series


#bullshittest
def _test_get_series():
    tvdb_key = '29E8EC8DF23A5918'
    api = tvdb_api.Tvdb(apikey=tvdb_key)    
    shows = ('friends','house','seinfeld','my name is earl', 'scrubs', 'cheers', 'dr who')
    for i in range(100):
        for  s in shows:
            print get_series(s)
            
