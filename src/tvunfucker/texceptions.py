#!/usr/bin/env python
# -*- coding: utf-8 -*-



class TVUFError(Exception):
    pass

class WTFException(TVUFError):
    #special exception, for special occasions
    pass

class IncompleteEpisodeError(TVUFError):
    """
    Occurs when LocalEpisode information is not sufficient to complete
    an operation.
    """
    pass

class InvalidArgumentError(TVUFError):
    pass

#fuck this
class NotADirectoryError(TVUFError):
    """
    def __init__(self, *args):
        super(NotADirectoryError, self).__init__(*args)
    """
    pass

class ShowNotFoundError(TVUFError):
    def __init__(self, msg, *args, **kwargs):
        msg = 'Show \'%s\' was not found on the TVDB' % msg
        TVUFError.__init__(self, msg, *args, **kwargs)

class EpisodeNotFoundError(TVUFError):
    def __init__(self, sow, season, ep, *args, **kwargs):
        msg = 'Series \'%s\', season %s, episode %s was not found on the TVDB' % (
            sow, season, ep)
        TVUFError.__init__(self, msg, *args, **kwargs)

class SeasonNotFoundError(TVUFError):
    def __init__(self, show, season, *args, **kwargs):
        msg = 'Series \'%s\', season %s was not found on the TVDB' % (
            show, season)
        TVUFError.__init__(self, msg, *args, **kwargs)        


class DatabaseAlreadyExistsError(TVUFError):
    pass        

class NoResultsError(TVUFError):
    pass

class NoIdInURLError(TVUFError):
    pass

class PoolError(TVUFError):
    pass

class PoolExhaustedError(PoolError):
    pass

class PutUnkeyedConnectionError(PoolError):
    pass
