from argparse import ArgumentParser
import logging, os

from . import appconfig, logger
from . import entrypoint


def main():
    parser = ArgumentParser()
    parser.add_argument(
        'directory', 
        help='Your TV directory. Can be any directory containing TV shows.'
        )
    parser.add_argument(
        '-u', '--update', dest='update_database',
        action='store_true', default=True,
        help='Only import episodes which don\'t already exist in database. (Default)'
        )
    parser.add_argument(
        '-r', '--reset', dest='reset_database',
        action='store_true', default=False,
        help='Overwrite existing database (if any) in directory.(overrides --update)'
        )
    parser.add_argument(
        '-e', '--extract-rars', dest='extract_rars',
        action='store_true', default=False,
        help='Extract episodes which are in rar format before scraping them.'\
            +'Rar files will be deleted afterwards.'
        )
    parser.add_argument(
        #TODO: This no work (cause value is set in __init__)
        '-l', '--log-file', dest='log_file', 
        help='Path to log file.'
        )
    parser.add_argument(
        '-v', '--verbosity', dest='log_level',
        default='INFO',
        help='Set log level.'\
        +'Available values (in order of highest -> lowest verbosity: '\
        +'DEBUG, INFO, WARNING, ERROR, FATAL'
        )
    parser.add_argument(
        '--clear-log-file', dest='clear_log_file', 
        action='store_true', default=False,
        help='Clear any existing log file.'
        )

    args = parser.parse_args()

    argsd = {}
    argsd['logging'] = {
        'level':args.log_level,
        'filename':args.log_file,
        'clear_log_file':args.clear_log_file
        }        
    argsd['database'] = {
        'reset':args.reset_database,
        'update':args.update_database
        }
    argsd['importer'] = {
        'unrar':args.extract_rars,
        'delete-rar':args.extract_rars
        }

    appconfig.import_to_runtime_parser(argsd)
    logger.log.setLevel(logging.__getattribute__(args.log_level.upper()))
    if args.clear_log_file:
        try:
            os.unlink(appconfig.get('logging', 'filename'))
        except: pass
    entrypoint.start_importer(args.directory)


    

if __name__ == '__main__':
    main()
