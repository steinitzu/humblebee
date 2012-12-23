import sys

from tvunfucker import importer

def main(argv=None):
    if argv is None:
        argv = sys.argv
    print argv
    imp = importer.Importer(argv[1])
    imp.start_import()

if __name__ == '__main__':
    main()
    
    
