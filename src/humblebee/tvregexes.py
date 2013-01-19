#!/usr/bin/env python
# -*- coding: utf-8 -*-


#Some of these are stolen from SickBeard

import re
from collections import namedtuple



separator = r'[\\\/\.\-_\s]'
namechars = r'[\w\.\s\,\!]'


#junk to be stripped from series names and stuff
junk = r'[\.\-_\[\]\(\)]'

def compile_regex(pattern):
    return re.compile(
        pattern % {'separator':separator, 'namechars':namechars},
        re.IGNORECASE | re.UNICODE | re.VERBOSE
        )

def compile_regexes(patterns):
    for regex in patterns:
        regex.pattern = compile_regex(regex.pattern)

class Regex(object):
    def __init__(self, alias, pattern):
        self.alias=alias
        self.pattern=pattern

tv_regexes = [
    Regex('standard_repeat',
    '''
    ^(?P<series_title>.+?)%(separator)s+                 #series name and sep
    s(?P<season_number>\d+)%(separator)s*                  #s01 and optional sep
    e(?P<ep_number>\d+)                                    #e01 and sep
    (%(separator)s+s(?P=season_number)%(separator)s*       #s01 and optional sep
    e(?P<extra_ep_number>\d+))+                            #e02 and sep
    %(separator)s*((?P<extra_info>.+?)                  #source/quality/etc
    ((?<!%(separator)s)-(?P<release_group>[^-]+))?)?$   #group
    '''),

    Regex('fov_repeat',
    '''
    ^(?P<series_title>.+?)%(separator)s+                # Show_Name and separator
    (?P<season_number>\d+)x                               # 1x
    (?P<ep_number>\d+)                                    # 02 and separator
    (%(separator)s+(?P=season_number)x                    # 1x
    (?P<extra_ep_number>\d+))+                            # 03/etc and separator
    %(separator)s*((?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<!%(separator)s)-(?P<release_group>[^-]+))?)?$  # Group
    '''),

    Regex('stupid_acronyms',
    '''
    (?P<release_group>.+?)-\w+?[\.]?
    s(?P<season_number>\d+)e(?P<ep_number>\d+)
    '''),    

    Regex('standard',
    # Show.Name.S01E02.Source.Quality.Etc-Group
    # Show Name - S01E02 - My Ep Name
    # Show.Name.S01.E03.My.Ep.Name
    # Show.Name.S01E02E03.Source.Quality.Etc-Group
    # Show Name - S01E02-03 - My Ep Name
    # Show.Name.S01.E02.E03
    '''
    ^((?P<series_title>.+?)%(separator)s+)?             # Show_Name and separator
    s(?P<season_number>\d+)%(separator)s*                 # S01 and optional separator
    e(?P<ep_number>\d+)                                   # E02 and separator
    ((%(separator)s*e|-)                               # linking e/- char
    (?P<extra_ep_number>(?!(1080|720)[pi])\d+))*          # additional E03/etc
    %(separator)s*((?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<!%(separator)s)-(?P<release_group>[^-]+))?)?$  # Group
    '''),
    
    Regex('fov',
    # Show_Name.1x02.Source_Quality_Etc-Group
    # Show Name - 1x02 - My Ep Name
    # Show_Name.1x02x03x04.Source_Quality_Etc-Group
    # Show Name - 1x02-03-04 - My Ep Name
    '''
    ^((?P<series_title>.+?)[\[. _-]+)?           # Show_Name and separator
    (?P<season_number>\d+)x                        # 1x
    (?P<ep_number>\d+)                             # 02 and separator
    (([. _-]*x|-)                               # linking x/- char
    (?P<extra_ep_number>
    (?!(1080|720)[pi])(?!(?<=x)264)             # ignore obviously wrong multi-eps
    \d+))*                                      # additional x03/etc
    [\]. _-]*((?P<extra_info>.+?)               # Source_Quality_Etc-
    ((?<![. _-])-(?P<release_group>[^-]+))?)?$  # Group
    '''),



    Regex('scene_date_format',
    # Show.Name.2010.11.23.Source.Quality.Etc-Group
    # Show Name - 2010-11-23 - Ep Name
    '''
    ^((?P<series_title>.+?)[. _-]+)?             # Show_Name and separator
    (?P<air_year>\d{4})[. _-]+                  # 2010 and separator
    (?P<air_month>\d{2})[. _-]+                 # 11 and separator
    (?P<air_day>\d{2})                          # 23 and separator
    [. _-]*((?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<![. _-])-(?P<release_group>[^-]+))?)?$  # Group
    '''),


    
    Regex('stupid',
    # tpz-abc102
    '''
    (?P<release_group>.+?)-\w+?[\. ]?           # tpz-abc
    (?!264)                                     # dont count x264
    (?P<season_number>\d{1,2})                     # 1
    (?P<ep_number>\d{2})$                          # 02
    '''),


    

    Regex('verbose',
    # Show Name Season 01 Episode 02 Ep Name
    # Show name Season 01 ep 02 ep name
    # separator
    #separators and anything after 'ep 02' is optional
    '''
    ^(?P<series_title>.+)%(separator)s?                # Show Name and separator
    season%(separator)s?                               # season and separator
    (?P<season_number>\d+)%(separator)s?
    (episode|ep)%(separator)s?                  # episode and separator
    (?P<ep_number>\d+)%(separator)s?                      # 02 and separator
    (((?P<extra_info>.+)$)|$)                         # Source_Quality_Etc-
    '''),


    Regex('season_ep_only',
    # S01E01
    # season 1 episode 2
    # s01xe02
    '''
    (s|season)%(separator)s*
    (?P<season_number>\d+)(%(separator)s|x)*
    (e|episode|ep)%(separator)s*
    (?P<ep_number>\d+)
    '''),
    

    Regex('season_only',
    # Show.Name.S01.Source.Quality.Etc-Group
    '''
    ^((?P<series_title>.+?)[. _-]+)?             # Show_Name and separator
    s(eason[. _-])?                             # S01/Season 01
    (?P<season_number>\d+)[. _-]*                  # S01 and optional separator
    [. _-]*((?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<![. _-])-(?P<release_group>[^-]+))?)?$  # Group
    '''),
          
    Regex('no_season_multi_ep',
    # Show.Name.E02-03
    # Show.Name.E02.2010
    '''
    ^((?P<series_title>.+?)[. _-]+)?             # Show_Name and separator
    (e(p(isode)?)?|part|pt)[. _-]?              # e, ep, episode, or part
    (?P<ep_number>(\d+|[ivx]+))                    # first ep num
    ((([. _-]+(and|&|to)[. _-]+)|-)                # and/&/to joiner
    (?P<extra_ep_number>(?!(1080|720)[pi])(\d+|[ivx]+))[. _-])            # second ep num
    ([. _-]*(?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<![. _-])-(?P<release_group>[^-]+))?)?$  # Group
    '''),

    Regex('bare_no_series',
    #102
    #1x02
    #1-02
    '''
    ^(?P<season_number>\d{1,2})(%(separator)s|x)*
    (?P<ep_number>\d{2})
    (%(separator)s+(?P<extra_info>(?!\d{3}%(separator)s+)[^-]+)
    (-(?P<release_group>.+))?)?$
    '''),
    

    Regex('no_season_general',
    # Show.Name.E23.Test
    # Show.Name.Part.3.Source.Quality.Etc-Group
    # Show.Name.Part.1.and.Part.2.Blah-Group
    '''
    ^((?P<series_title>.+?)[. _-]+)?             # Show_Name and separator
    (e(p(isode)?)?|part|pt)[. _-]?              # e, ep, episode, or part
    (?P<ep_number>(\d+|([ivx]+(?=[. _-]))))        # first ep num
    ([. _-]+((and|&|to)[. _-]+)?                # and/&/to joiner
    ((e(p(isode)?)?|part|pt)[. _-]?)            # e, ep, episode, or part
    (?P<extra_ep_number>(?!(1080|720)[pi])
    (\d+|([ivx]+(?=[. _-]))))[. _-])*           # second ep num
    ([. _-]*(?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<![. _-])-(?P<release_group>[^-]+))?)?$  # Group
    '''),
    
    Regex('bare',
    # Show.Name.102.Source.Quality.Etc-Group
    '''
    ^(?P<series_title>.+?)[. _-]+                        # Show_Name and separator
    (?P<season_number>\d{1,2})                             # 1     
    (?P<ep_number>\d{2})                                   # 02 and separator
    ([. _-]+(?P<extra_info>(?!\d{3}[. _-]+)[^-]+)       # Source_Quality_Etc-
    (-(?P<release_group>.+))?)?$                        # Group
    '''),

    Regex('bare_no_series',
    #102
    #1x02
    #1-02
    '''
    ^(?P<season_number>\d{1,2})(%(separator)s|x)*
    (?P<ep_number>\d{2})
    (%(separator)s+(?P<extra_info>(?!\d{3}%(separator)s+)[^-]+)
    (-(?P<release_group>.+))?)?$
    '''),

    Regex('bare_no_series',
    # 102.ep.name.Etc-Group
    '''
    ^(?P<season_number>\d{1,2})                    
    (?P<ep_number>\d{2})
    (%(separator)s+(?P<extra_info>(?!\d{3}%(separator)s+)[^-]+)
    (-(?P<release_group>.+))?)?$    
    '''),

    Regex('no_season',
    # Show Name - 01 - Ep Name
    # 01 - Ep Name
    '''
    ^((?P<series_title>.+?)[. _-]+)?             # Show_Name and separator
    (?P<ep_number>\d{2})                           # 02
    [. _-]+((?P<extra_info>.+?)                 # Source_Quality_Etc-
    ((?<![. _-])-(?P<release_group>[^-]+))?)?$  # Group
    '''),          

    Regex('just_season_dir',
    #s01
    #season01
    #season[separator]01
    '''
    ^(season|s)(%(separator)s|)(?P<season_number>\d+)$
    '''),

    
    #Hold on
    Regex('standardish_weird',
    #shownames01e02somecrap
    #showname[separator(or not)]s01e02
    '''
    ^(?P<series_title>.+?)%(separator)s?  #showname can be whatever
    (s|S)(?P<season_number>\d+)               #s01 || S01
    (e|E)(?P<ep_number>\d+)                   #e02 || E02    
    ''')
    
    
]

compile_regexes(tv_regexes)

    



tv_regexes_old = [
    #Series name S01E01 i dont care
    #series.name.s01e01.i.dont.care
    #other similarly formed (i.e. everything before s01e01 is treated as series name)
    compile_regex(r'(?P<series>%(namechars)s*)[\\\/\.\-_\s]*[Ss](?P<season>\d+)[eE](?P<episode>\d+)'),
    #series name 01x01 i don't care
    compile_regex(r'(?P<series>%(namechars)s*)[\\\/\.\-_\s]*(?P<season>\d+)[xX](?P<episode>\d+)'),
    #series name season 1 episode 1
    compile_regex(
        r'(?P<series>[\w\.\s]+)%(separator)sseason%(separator)s(?P<season>\d+)'
        +'%(separator)sepisode%(separator)s(?P<episode>\d+)'),
    #proper season and ep
    #s01e01
    compile_regex(r'[sS](?P<season>\d+)[eE](?P<episode>\d+)'),
    #season 1 episode 1
    compile_regex(r'season%(separator)s*(?P<season>\d+)%(separator)s*episode%(separator)s(?P<episode>\d+)'),
    #series name season 1
    compile_regex(r'(?P<series>[\w\.\s]+)%(separator)sseason%(separator)s(?P<season>\d+)'),
    #short season only
    #s01
    compile_regex(r'%(separator)s|^[sS](?P<season>\d+)'),
    #short ep only
    compile_regex(r'%(separator)s|^[eE](?P<episode>\d+)'),
    #verbose season only
    #season 1
    #some stuff season 1    
    compile_regex(r'%(separator)s|^season%(separator)s(?P<season>\d+)'),
    #numbered episode
    #episode 1.avi
    compile_regex(r'%(separator)s|^episode[\\\/\.\-_\s]*(?P<episode>\d+)'),
    #only series
    compile_regex(r'(?P<series>%(namechars)s+).+season')
    ]






                
    
