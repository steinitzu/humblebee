#!/usr/bin/env python
# -*- coding: utf-8 -*-



class TVUFError(Exception):
    pass

class IncompleteEpisodeError(TVUFError):
    """
    Occurs when LocalEpisode information is not sufficient to complete
    an operation.
    """
    def __init__(self, *args):
        super(IncompleteEpisodeError, self).__init__(*args)

class InvalidArgumentError(TVUFError):
    def __init__(self, *args):
        super(InvalidArgumentError, self).__init__(*args)

#fuck this
class NotADirectoryError(TVUFError):
    def __init__(self, *args):
        super(NotADirectoryError, self).__init__(*args)
