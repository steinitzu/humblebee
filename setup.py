
#!/usr/bin/env python
#encoding:utf-8

from setuptools import setup

setup(
    name='humblebee',
    version='1.10',
    description='A scraper for TV shows.',
    author='Steinthor Palsson',
    author_email='steinitzu@gmail.com',
    url='https://github.com/steinitzu/humblebee',
    license='MIT',

    packages=[
        'humblebee', 
        ],
    package_data = {'' : ['default.cfg', 'schema.sql', 'cacert.txt']},    


    entry_points={
        'console_scripts': [
            'humblebee = humblebee.cli:main'
            ]
        },    
    
    install_requires=[
        'httplib2', 
        'pyUnRAR2',
        'send2trash',
        'unidecode',
        'gnarlytvdb',
        'xmltodict',
        ]
    )
