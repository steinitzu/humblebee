#!/usr/bin/env python
# -*- coding: utf-8 -*-



class TVUFError(Exception):
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
