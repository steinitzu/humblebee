# Humblebee  (version 1.10) #

Humblebee is a scraper and renamer/organizer for TV shows.  
It is made with the intention to automatically organize the most disorganized collections without any manual user input.

Keep in mind, this program is in development stages and there will be (potentially dangerous) bugs.

## Features ##
* Parse tv show filenames and gather metadata from thetvdb
* Create a portable, local database of metadata
* Rename and organize tv shows based on metadata
* Create a virtual TV directory structures using symlinks
* Extract rar-ed scene release episodes
* Locate duplicate episodes and determine which one has better video quality

## Install ## 
I will assume a debian-based environment (e.g. ubuntu, mint, etc) for this guide. Adapt following commands to your distro's package management system.  

Easiest way to install is by using pip.  
If you don't have pip, install it with:
    
    sudo apt-get install python-pip
    
Humblebee also requires a couple of extra packages for all features to work, lets grab them:

    sudo apt-get install mediainfo unrar
    
Now we install can humblebee using:

    sudo pip install humblebee        
    
That's it. Now lets see how we use this thing.  


## Usage ##
Humblebee comes with a command line interface with various options. To see a description the available options, use:
    
    humblebee --help
    
Now one common use case would be to scrape your disorganized TV directory and make a structured presentation of it with symlinks. This can be achieved with:

    humblebee -s /home/user/TV /home/user/cleanTV
    
`/home/user/TV` being your original TV directory and `/home/user/cleanTV` where the symlinks are made.  
The default naming scheme for renamed directory is `Series Name/season 01/Series Name s01e02 Episode Name.mkv`. Currently it's the only naming scheme available, but more will come in future releases.

You can substitute `-s` for `-r` if you'd like humblebee to move your files to `/home/user/cleanTV` instead of making symlinks. If you do this, a second database is made in `/home/user/cleanTV`

Scraping can take a while depending on the size of your collection, so grab a soda.

## How can I help? ##
Easiest way to help is to simply use the program and report any bugs and issues you encounter here https://github.com/steinitzu/humblebee/issues  
You may also submit code patches and documentation to the official repo https://github.com/steinitzu/humblebee   
If you improve something, it will most likely be accepted.


...to be continued


### TODO ###
* Documentation
* support Windows
* Test cases
* Take over world


