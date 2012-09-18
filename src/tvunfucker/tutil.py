#!/usr/bin/env python
# -*- coding: utf-8 -*-



class InvalidArgumentError(Exception):

    def __init__(self, *args):
        super(InvalidArgumentError, self).__init__(*args)


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
               
     
