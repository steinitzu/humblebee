from optparse import OptionParser




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
    (options, args) = parser.parse_args()
        
if __name__ == '__main__':
    main()
