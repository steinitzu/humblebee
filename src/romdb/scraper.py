import os, re

import tvdb_api

from romlog import *
import romexception
import romdb

#paths to media folders
sources = {
    'tv' : ['/media/boneraper'],
    'movies' : ['/media/heimdallur/movies']
    }
video_files = ['mkv','avi','mpeg','mpg','mp4','wmv'] #add as needed (or do something different)


"""
Should handle shit well.
First, just get a list of first level directories in the source (single files in sep list)
and then, check all these subdir names weather they are single series dirs
and then, put all single series dirs in a list and all non-series (mixed shit like incoming) in another list
and then, handle single series dirs like single series and mixed things as mixed things
now code that shit
"""


def traverse_source(source):
    """
    Path to source -> yields abs paths subdirectories
    """
    for root,dirs,files in os.walk(source):
        for dir_ in dirs:
            yield os.path.join(root,dir_)

def get_media_files(directory):
    """
    Returns a list of abs paths to media files in given directory.
    """
    #TODO: code it
    dirname = os.path.split(directory)
    return dirname

#TVMODE
def get_tvdb_api():
    """
    Gets a new instance of the Tvdb class using the api key
    hardcoded in the package.
    """
    return tvdb_api.Tvdb(apikey=romdb.tvdb_key)

#TVMODE
def directory_is_series(directory):
    """
    Raises an OSEerror in case of trouble accessing directory.\n
    Check weather given directory is a series (e.g. contains a one tv show).\n
    If true -> all subdirectories in [directory] can be handled
    like they're part of the same show.\n
    Please use absolute paths for the greater good.\n
    \n
    Returns either False or a tvdb_api.Series object.
    """    
    if not os.path.isdir(directory):
        #TODO:Check here or in caller?
        return False    

    
    #but how can I know that?
    #0. strip all symbols and stuff from the name
    #1. search tvdb
    #2. ???
    #3. PROFIT!    

#@log_info
def get_series_name_from_file_name(dirname):
    """
    Attempt to extract the series name from the given directory or file name.\n
    This will always work for names which follow the scene naming conventions of:
    Episode.name.S##E##.Format-Group\n
    Will also strip all kinds of other junk from the string.\n
    The goal is that the string is searchable from tvdb.
    """
    dirname = dirname.lower()
    result = re.sub(r'\{.+\}', '', dirname)
    result = re.sub(r'\[.+\]', '', result) #dno if need        
    result = re.split(r'\.s\d+', result)[0]
    result = result.strip()

    result = result.replace('.', ' ')
    result = result.strip('-')
    return result.title()
    
def test():
    
    #for dir_ in traverse_source(sources['tv'][0]):
    #    print get_media_files(dir_)
    print get_series_name_from_file_name('my.name.is.earl.s01e05')


if __name__ == '__main__':
    test()
        





