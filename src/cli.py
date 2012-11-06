from optparse import OptionParser
import logging

from tvunfucker.chainwrapper import create_database
from tvunfucker.texceptions import *




def main():
    parser = OptionParser()
    pa = parser.add_option
    pa(
        '-s', 
        '--source-directory', 
        dest='source_directory',
        help='A directory with TV shows you want to scrape.',
        metavar='PATH'
        )
    pa(
        '-m',
        '--mount-point',
        dest='mount_point',
        help='Mountpoint for the virtual filesystem. (Any empty directory you have write access to).',
        metavar='PATH'
        )
    pa(
        '-r',
        '--reset-database',
        dest='reset_database',
        help='Pre-existing database file in given --source-directory will be deleted and the database will be re-created from scratch.'
        )
    pa(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        help='verbose output (log level INFO), this prints lots of details.'
        )
    pa(
        '-V',
        '--very-verbose',
        action='store_true',
        dest='very_verbose',
        help='even more verbose (log level DEBUG). This is intended for developers and people who like to read irrelevant shit.'
        )
    (options, args) = parser.parse_args()

    log = logging.getLogger('tvunfucker')

    if options.verbose:
        log.setLevel(logging.INFO)
    elif options.very_verbose:
        log.setLevel(logging.DEBUG)

    if options.source_directory:
        create_database(options.source_directory)
                
        
        
if __name__ == '__main__':
    main()
