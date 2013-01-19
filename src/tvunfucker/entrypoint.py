from . import importer

def start_importer(directory, dest_directory):
    """
    start_importer(directory)
    Start a new Importer with current cfg options.
    """
    imp = importer.Importer(directory, dest_directory)
    imp.do_import()
