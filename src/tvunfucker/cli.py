from argparse import ArgumentParser

from .importer import Importer


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '-l', '--log-file', dest='log_file', 
        help='Path to log file.'
        )
    parser.add_argument(
        'directory', 
        help='Your TV directory. Can be any directory containing TV shows.'
        )
    parser.add_argument(
        '-r', '--reset-database', dest='reset_database',
        action='store_true', default=False,
        help='Overwrite existing database (if any) in directory.'
        )
    parser.add_argument(
        '-v', '--verbosity', dest='log_level',
        default='INFO',
        help='Set log level.'\
        +'Available values (in order of highest -> lowest verbosity: '\
        +'DEBUG, INFO, WARNING, ERROR, FATAL'
        )

    args = parser.parse_args()

if __name__ == '__main__':
    main()
