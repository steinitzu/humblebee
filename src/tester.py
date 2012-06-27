import tvunfucker

from tvunfucker import chainwrapper, parser

ep = chainwrapper.api['house'][5][5]
eppi = parser.LocalEpisode('blehbleh')
eppi['tvdb_ep'] = ep

source = chainwrapper.EpisodeSource('/home/steini/tvtesttree')
source.initialize_database()
source.add_series_to_db(eppi)
