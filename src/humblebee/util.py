#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime
import os, sys, re, shutil
from unidecode import unidecode

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

def scene_style(string):
    """
    Return given string in scene style.
    WIth spaces replaced with '.' and lowercase.
    """
    if string is None:
        return
    return '.'.join(string.split())

def soft_unlink(fn):
    """
    os.unlink which ignores 'file not exist' errors.
    """
    try:
        os.unlink(fn)
    except OSError as e:
        if e.errno == 2:
            pass
        else:
            raise


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
    elif string.lower() == 'true':
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
    raise NotImplementedError(
        'This function has been killed, use "components" instead.'
        )
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

def samefile(p1, p2):
    """Safer equality for paths."""
    return shutil._samefile(syspath(p1), syspath(p2))

def prune_dirs(path, root=None, clutter=('.DS_Store', 'Thumbs.db')):
    """If path is an empty directory, then remove it. Recursively remove
    path's ancestry up to root (which is never removed) where there are
    empty directories. If path is not contained in root, then nothing is
    removed. Filenames in clutter are ignored when determining
    emptiness. If root is not provided, then only path may be removed
    (i.e., no recursive removal).
    """
    path = normpath(path)
    if root is not None:
        root = normpath(root)

    ancestors = ancestry(path)
    if root is None:
        # Only remove the top directory.
        ancestors = []
    elif root in ancestors:
        # Only remove directories below the root.
        ancestors = ancestors[ancestors.index(root)+1:]
    else:
        # Remove nothing.
        return

    # Traverse upward from path.
    ancestors.append(path)
    ancestors.reverse()
    for directory in ancestors:
        directory = syspath(directory)
        if not os.path.exists(directory):
            # Directory gone already.
            continue

        if all(fn in clutter for fn in os.listdir(directory)):
            # Directory contains only clutter (or nothing).
            try:
                shutil.rmtree(directory)
            except OSError:
                break
        else:
            break

def make_symlink(target, link, overwrite=False):
    """
    Make symlink and all dirs leading up to it.
    OSError 17 (file exists) will be ignored.
    If overwrite, existing symlink at `link` will be overwritten.
    """
    target = syspath(target)
    link = syspath(link)
    dirs = os.path.split(link)[0]
    if dirs:
        safe_make_dirs(dirs)
    try:        
        os.symlink(target, link)
    except OSError as e:
        if e.errno == 17:
            if overwrite and os.path.islink(link):
                os.unlink(link)
                os.symlink(target, link)
        else:
            raise        

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

def components(path, pathmod=None):
    """Return a list of the path components in path. For instance:

       >>> components('/a/b/c')
       ['a', 'b', 'c']

    The argument should *not* be the result of a call to `syspath`.
    """
    pathmod = pathmod or os.path
    comps = []
    ances = ancestry(path, pathmod)
    for anc in ances:
        comp = pathmod.basename(anc)
        if comp:
            comps.append(comp)
        else:  # root
            comps.append(anc)

    last = pathmod.basename(path)
    if last:
        comps.append(last)

    return comps

def posixpath(path):
    """
    Replace backslashes with slashes and nothing else.
    """
    return path.replace('\\', '/')

def prune_dirs(path, root=None, clutter=('.DS_Store', 'Thumbs.db')):
    """If path is an empty directory, then remove it. Recursively remove
    path's ancestry up to root (which is never removed) where there are
    empty directories. If path is not contained in root, then nothing is
    removed. Filenames in clutter are ignored when determining
    emptiness. If root is not provided, then only path may be removed
    (i.e., no recursive removal).
    """
    path = normpath(path)
    if root is not None:
        root = normpath(root)

    ancestors = ancestry(path)
    if root is None:
        # Only remove the top directory.
        ancestors = []
    elif root in ancestors:
        # Only remove directories below the root.
        ancestors = ancestors[ancestors.index(root)+1:]
    else:
        # Remove nothing.
        return

    # Traverse upward from path.
    ancestors.append(path)
    ancestors.reverse()
    for directory in ancestors:
        directory = syspath(directory)
        if not os.path.exists(directory):
            # Directory gone already.
            continue

        if all(fn in clutter for fn in os.listdir(directory)):
            # Directory contains only clutter (or nothing).
            try:
                shutil.rmtree(directory)
            except OSError:
                break
        else:
            break

#blatantly stolen from beets
#string distance stuff

# Parameters for string distance function.
# Words that can be moved to the end of a string using a comma.
SD_END_WORDS = ['the', 'a', 'an']
# Reduced weights for certain portions of the string.
SD_PATTERNS = [
    (r'^the ', 0.1),
    #(r'[\[\(]?(ep|single)[\]\)]?', 0.0),
    #(r'[\[\(]?(featuring|feat|ft)[\. :].+', 0.1),
    #(r'\(.*?\)', 0.3),
    #(r'\[.*?\]', 0.3),
    (r'(, )?(pt\.|part) .+', 0.2),
]
# Replacements to use before testing distance.
SD_REPLACE = [
    (r'&', 'and'),
]

def levenshtein(s1, s2):
    """A nice DP edit distance implementation from Wikibooks:
    http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/
    Levenshtein_distance#Python
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s1:
        return len(s2)

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def _string_dist_basic(str1, str2):
    """Basic edit distance between two strings, ignoring
    non-alphanumeric characters and case. Comparisons are based on a
    transliteration/lowering to ASCII characters. Normalized by string
    length.
    """
    str1 = unidecode(str1)
    str2 = unidecode(str2)
    str1 = re.sub(r'[^a-z0-9]', '', str1.lower())
    str2 = re.sub(r'[^a-z0-9]', '', str2.lower())
    if not str1 and not str2:
        return 0.0
    return levenshtein(str1, str2) / float(max(len(str1), len(str2)))

def string_dist(str1, str2):
    """Gives an "intuitive" edit distance between two strings. This is
    an edit distance, normalized by the string length, with a number of
    tweaks that reflect intuition about text.
    """
    str1 = str1.lower()
    str2 = str2.lower()

    # Don't penalize strings that move certain words to the end. For
    # example, "the something" should be considered equal to
    # "something, the".
    for word in SD_END_WORDS:
        if str1.endswith(', %s' % word):
            str1 = '%s %s' % (word, str1[:-len(word)-2])
        if str2.endswith(', %s' % word):
            str2 = '%s %s' % (word, str2[:-len(word)-2])

    # Perform a couple of basic normalizing substitutions.
    for pat, repl in SD_REPLACE:
        str1 = re.sub(pat, repl, str1)
        str2 = re.sub(pat, repl, str2)

    # Change the weight for certain string portions matched by a set
    # of regular expressions. We gradually change the strings and build
    # up penalties associated with parts of the string that were
    # deleted.
    base_dist = _string_dist_basic(str1, str2)
    penalty = 0.0
    for pat, weight in SD_PATTERNS:
        # Get strings that drop the pattern.
        case_str1 = re.sub(pat, '', str1)
        case_str2 = re.sub(pat, '', str2)

        if case_str1 != str1 or case_str2 != str2:
            # If the pattern was present (i.e., it is deleted in the
            # the current case), recalculate the distances for the
            # modified strings.
            case_dist = _string_dist_basic(case_str1, case_str2)
            case_delta = max(0.0, base_dist - case_dist)
            if case_delta == 0.0:
                continue

            # Shift our baseline strings down (to avoid rematching the
            # same part of the string) and add a scaled distance
            # amount to the penalties.
            str1 = case_str1
            str2 = case_str2
            base_dist = case_dist
            penalty += weight * case_delta
    dist = base_dist + penalty

    return dist
