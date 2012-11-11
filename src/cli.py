from optparse import OptionParser
import logging, os
from threading import Thread

from tvunfucker.chainwrapper import create_database, scrape_source, EpisodeSource
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
        '-n',
        '--no-scan',
        help='Do not scan the given source directory (-s) but only mount its database (if any). Use with -m',
        action='store_true',
        default=False
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
        metavar='STRING'
        )
    pa(
        '-a',
        '--allow-other',
        dest='allow_other',
        help='Pass "allow_other" options to the fuse virtual filesystem. This means that other users than the one who mounted it can access the filesystem (if you mount as root, or want to share the fs using samba, you probably want this).\n This requires the "allow_other_user" option to be enabled in /etc/fuse.conf.',
        action='store_true',
        default=False
        )
    (options, args) = parser.parse_args()

    log = logging.getLogger('tvunfucker')
    if options.log_level:
        log.setLevel(
            logging.__getattribute__(options.log_level.upper())
            )
    else:
        log.setLevel(logging.WARNING)

    source = None
    if options.source_directory:
        try:
            source = create_database(
                options.source_directory,
                force=options.reset_database
                )
        except DatabaseAlreadyExistsError:
            source = EpisodeSource(
                options.source_directory
                )
        if not options.no_scan:
            t = Thread(target=scrape_source, args=(source,))
            t.start()        
        if options.mount_point:
            fg = options.log_level.upper() == 'DEBUG'            
            mount_db_filesystem(
                source, 
                options.mount_point, 
                foreground=fg,
                allow_other=options.allow_other
                )
    elif options.mount_point:
        raise InvalidArgumentError(
            'You must specify a source directory ( -s )'
            )
        
        
if __name__ == '__main__':
    main()
