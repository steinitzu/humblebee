from optparse import OptionParser
import logging
import sys

from tvunfucker.chainwrapper import create_database, scrape_source, EpisodeSource
from tvunfucker.texceptions import DatabaseAlreadyExistsError


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
        '-r',
        '--reset-database',
        dest='reset_database',
        help='Pre-existing database file in given --source-directory will be deleted and the database will be re-created from scratch.',
        action='store_true', 
        default=False
        )
    pa(
        '-l',
        '--log-level',
        dest='log_level',
        help='Log level. Available options in order of least verbose to most verbose: CRITICAL, ERROR, WARNING, INFO, DEBUG. (Default: WARNING).\nKeep in mind that DEBUG will create a massive log with large collections.',
        metavar='STRING',
        default='WARNING'
        )        
    (options, args) = parser.parse_args()

    log = logging.getLogger('tvunfucker')
    log.setLevel(logging.__getattribute__(options.log_level.upper()))    

    try:
        source = create_database(options.source_directory, options.reset_database)
    except DatabaseAlreadyExistsError as e:
        source = EpisodeSource(options.source_directory)
    log.info('Will now begin scraping directory: %s', options.source_directory)
    scrape_source(source)


if __name__ == '__main__':
    main()    
