import os, sys

from UnRAR2 import RarFile
from UnRAR2.rar_exceptions import ArchiveHeaderBroken, InvalidRARArchive, FileOpenError, IncorrectRARPassword, InvalidRARArchiveUsage

from .texceptions import RARError

error = (
    ArchiveHeaderBroken,
    InvalidRARArchiveUsage,
    FileOpenError,
    IncorrectRARPassword,
    InvalidRARArchiveUsage
    )



def unrar_file(path, out_dir=None):
    """
    unrar_episode(path, out_dir)
    Path should be a working path to a rar file.
    Extract given file to out_dir.
    If |out_dir| is None it becomes the same
    directory where |path| resides.
    If path is a directory out_dir will be the same
    """   
    if out_dir is None:
        if os.path.isdir(path):
            out_dir = path
        else:
            out_dir = os.path.dirname(path)
    try:
        rf = RarFile(path)
    except error as e:
        raise RARError(
            'Failed to open file "%s"' % path), None, sys.exc_info()[2]
    try:
        rf.extract(path=out_dir)
    except error as e:
        raise RARError(
            'Failed to extract file "%s"' % path), None, sys.exc_info()[2]
    
        

