from . import importer

def start_importer(directory):
    """
    start_importer(directory)
    Start a new Importer with current cfg options.
    """
    imp = importer.Importer(directory)
    imp.start_import()
