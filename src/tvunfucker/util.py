#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime


def zero_prefix_int(num):
    """
    zero_prefix_number(int) -> str\n
    Puts a zero in fron of 1 digit numbers.\n
    otherwise just returns the int
    """
    strnum = str(num)
    if len(strnum) == 1:
        return '0'+strnum
    return num

def timestamp(dt):
    return mktime(dt.timetuple())

def safe_strpdate(s):
    """
    Save as in: doesn't shit bricks on empty values.
    """
    if not s:
        return None
    return datetime.strptime(s, '%Y-%m-%d').date()

def ensure_utf8(value):
    if not isinstance(value, basestring):
        raise ValueError(
            'Arg 0 must be a string type. You gave \'%s\' (type %s)' %
            (value, type(value)
             ))
    if value == '':
        return u''
    if isinstance(value, unicode):
        return value
    return value.decode('utf-8')
