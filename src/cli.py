from optparse import OptionParser
import logging, os

from tvunfucker.chainwrapper import get_database
from tvunfucker.texceptions import *
from tvunfucker.thefuse import mount_db_filesystem




def main():
    parser = OptionParser()
    pa = parser.add_option
    pa(
        '-s', 
        '--source-directory', 
        dest='source_directory',
        help='A directory with TV shows you want to scrape.',
        metavar='DIRECTORY'
        )
    pa(
        '-m',
        '--mount-point',
        dest='mount_point',
        help='Mountpoint for the virtual filesystem. (Any empty directory you have write access to).',
        metavar='DIRECTORY'
        )
    pa(
        '-r',
        '--reset-database',
        dest='reset_database',
        help='Pre-existing database file in given --source-directory will be deleted and the database will be re-created from scratch.'
        )
    pa(
        '-l',
        '--log-level',
        dest='log_level',
        help='Log level. Available options in order of least verbose to most verbose: CRITICAL, ERROR, WARNING, INFO, DEBUG. (Default: WARNING)',
        metavar='STRING'
        )
    (options, args) = parser.parse_args()

    log = logging.getLogger('tvunfucker')
    if options.log_level:
        log.setLevel(
            logging.__getattribute__(options.log_level.upper())
            )
    else:
        log.setLevel(logging.WARNING)

    dbfile = os.path.join(options.source_directory, '.tvunfucker.sqlite')
    source = None
    if options.source_directory:
        if not os.path.exists(dbfile) or options.reset_database:
            source = get_database(options.source_directory)            
        else:
            source = get_database(options.source_directory, create=False)

    if options.mount_point:
        mount_db_filesystem(source, options.mount_point, foreground=True)
        
        
        
                
        
        
if __name__ == '__main__':
    main()
