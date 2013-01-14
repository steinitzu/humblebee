import os

from UnRAR2 import RarFile



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
    rf = RarFile(path)
    rf.extract(path=out_dir)

