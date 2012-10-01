#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime

from texceptions import InvalidArgumentError

#should be in __init__
program_name = 'tvunfucker'


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

def split_path(path):
    return path.strip('/').split('/')



def type_safe(
    arg,
    expected_type,
    arg_num=0,
    error_message=None
    ):
    """
    A pseudo type safety function.\n
    arg: the object you want to check\n
    expected_type: the desired type of arg\n
    arg_num=0: the number of this argument in the calling function\n
    error_message=None: Message raised in case the type is wrong.
    Defaults to 'Invalid type for argument %d. Got \'%s\' expected \'%s\'.'\n
    \n
    Raises an InvalidArgumentError or returns True
    """    
    if not error_message:
        error_message = (
            'Invalid type for argument %d. Got \'%s\' expected \'%s\'.' %
            (arg_num, type(arg), expected_type)
            )        
    if not isinstance(arg, expected_type):
        raise (InvalidArgumentError(error_message))
    return True
