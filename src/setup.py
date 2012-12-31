#!/usr/bin/env python
#encoding:utf-8

from setuptools import setup

setup(
    name='tvunfucker',
    version='0.5',
    description='A scraper for TV shows.',
    author='Steinthor Palsson',
    author_email='steinitzu@gmail.com',
    url='https://github.com/steinitzu/romdb',
    license='MIT',

    include_package_data=True,
    
    packages=[
        'tvunfucker', 
        'tvunfucker.tvdb_api'
        ],
    
    package_data = {'tvunfucker' : ['default.cfg', 'schema.sql']},
    
    entry_points={
        'console_scripts': [
            'tvunfucker = tvunfucker.cli:main'
            ]
        },    
    
    install_requires=[
        'httplib2' #for bing api
        ]
    )
