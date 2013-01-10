#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime
import os, sys

from texceptions import InvalidArgumentError


def get_prog_home_dir(program_name):
    if sys.platform == 'win32':
        return os.path.join(
            os.environ['APPDATA'],
            program_name
            )
    else:
        return os.path.join(
            os.path.expanduser('~'),
            '.'+program_name
            )    

def replace_bad_chars(string):
    """
    Remove chars that can cause problems in filenames
    with some platforms and file managers.
    """
    chars = ('?', ':', '/', '\\', '|', '<', '>')
    nstring = string
    for ch in chars:
        nstring = nstring.replace(ch, '')
    return nstring


def fndotify(string, keep_bad_chars=False):
    """
    Lower case and replace spaces with dots.
    Also does a 'replace_bad_chars'.
    Use keep_bad_chars=True if you don't want that.
    """
    string = replace_bad_chars(string)
    return string.lower().replace(' ', '.')

def zero_prefix_int(num):
    """
    zero_prefix_number(int) -> str\n
    Puts a zero in fron of 1 digit numbers.\n
    otherwise just returns the int
    """
    strnum = str(num)
    if len(strnum) == 1:
        return '0'+strnum
    return strnum

def timestamp(dt):
    return mktime(dt.timetuple())

def str_to_bool(string):
    """
    str_to_bool('False') -> False
    str_to_bool('True') -> False
    str_to_bool('true') -> True
    """
    if isinstance(string, bool):
        return string
    if string.lower() == 'false':
        return False
    elif string.lower() == 'True':
        return True
    else:
        raise ValueError('"%s" can not be converted to bool' % string)

def safe_strpdate(s):
    """
    Save as in: doesn't shit bricks on empty values.
    """
    if not s:
        return None
    return datetime.strptime(s, '%Y-%m-%d').date()

def ensure_utf8(value):
    if value is None: return None
    if not isinstance(value, basestring):
        raise ValueError(
            'Arg 0 must be a string type. You gave \'%s\' (type %s)' %
            (value, type(value)
             ))
    if value == '':
        return u''
    try:
        return value.decode('utf-8')
    except UnicodeEncodeError:
        return value.encode('utf-8').decode('utf-8')
    #if isinstance(value, unicode):
    #    return value
    #return value.decode('utf-8')

WINDOWS_MAGIC_PREFIX = u'\\\\?\\'

def _fsencoding():
    """Get the system's filesystem encoding. On Windows, this is always
    UTF-8 (not MBCS).
    """
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    if encoding == 'mbcs':
        # On Windows, a broken encoding known to Python as "MBCS" is
        # used for the filesystem. However, we only use the Unicode API
        # for Windows paths, so the encoding is actually immaterial so
        # we can avoid dealing with this nastiness. We arbitrarily
        # choose UTF-8.
        encoding = 'utf8'
    return encoding

def bytestring_path(path, pathmod=None):
    """Given a path, which is either a str or a unicode, returns a str
    path (ensuring that we never deal with Unicode pathnames).
    """
    pathmod = pathmod or os.path
    windows = pathmod.__name__ == 'ntpath'

    # Pass through bytestrings.
    if isinstance(path, str):
        return path

    # On Windows, remove the magic prefix added by `syspath`. This makes
    # ``bytestring_path(syspath(X)) == X``, i.e., we can safely
    # round-trip through `syspath`.
    if windows and path.startswith(WINDOWS_MAGIC_PREFIX):
        path = path[len(WINDOWS_MAGIC_PREFIX):]

    # Try to encode with default encodings, but fall back to UTF8.
    try:
        return path.encode(_fsencoding())
    except (UnicodeError, LookupError):
        return path.encode('utf8')

def syspath(path, pathmod=None):
    """Convert a path for use by the operating system. In particular,
    paths on Windows must receive a magic prefix and must be converted
    to unicode before they are sent to the OS.
    """
    pathmod = pathmod or os.path
    windows = pathmod.__name__ == 'ntpath'

    # Don't do anything if we're not on windows
    if not windows:
        return path

    if not isinstance(path, unicode):
        # Beets currently represents Windows paths internally with UTF-8
        # arbitrarily. But earlier versions used MBCS because it is
        # reported as the FS encoding by Windows. Try both.
        try:
            path = path.decode('utf8')
        except UnicodeError:
            # The encoding should always be MBCS, Windows' broken
            # Unicode representation.
            encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
            path = path.decode(encoding, 'replace')

    # Add the magic prefix if it isn't already there
    if not path.startswith(WINDOWS_MAGIC_PREFIX):
        path = WINDOWS_MAGIC_PREFIX + path

    return path

def normpath(path):
    """Provide the canonical form of the path suitable for storing in
    the database.
    """
    path = syspath(path)
    path = os.path.normpath(os.path.abspath(os.path.expanduser(path)))
    return bytestring_path(path)

def split_path(path):
    return path.strip('/').split('/')


def split_root_dir(path, root):
    """
    split_root_dir(path, root) -> (root, path[root:])
    Split `root` from `path` and return both.
    """
    root = normpath(root)
    r = os.path.relpath
    pj = os.path.join
    if path.startswith(root):
        path = path[len(root):].strip('\\/')
    return normpath(root), bytestring_path(r(pj(root, path), root))  

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


def safe_make_dirs(path):
    """
    _safe_make_dirs(path)
    os.makedir but suppresses errors when dir already exists.
    All other errors are raised as normal.
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == 17: #file exists
            pass
        else:
            raise


def ancestry(path, pathmod=None):
    """Return a list consisting of path's parent directory, its
    grandparent, and so on. For instance:

       >>> ancestry('/a/b/c')
       ['/', '/a', '/a/b']

    The argument should *not* be the result of a call to `syspath`.
    """
    pathmod = pathmod or os.path
    out = []
    last_path = None
    while path:
        path = pathmod.dirname(path)

        if path == last_path:
            break
        last_path = path

        if path: # don't yield ''
            out.insert(0, path)
    return out
