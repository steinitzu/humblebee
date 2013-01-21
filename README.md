# Humblebee  (version 1.06) #

Humblebee is a scraper and renamer for TV shows.
It handles many naming schemes and the most odd directory structures.

## Features ##
* Parse tv show filenames and gather metadata from thetvdb
* Create a portable, local database of metadata
* Rename and organize tv shows based on metadata
* Create a virtual TV directory structures using symlinks
* Extract rar-ed scene release episodes


## Install and usage ## 
Easiest way to install is by using pip.  
On ubuntu, mint, debian and other debian based distros, pip can be install with the following command:
    
    sudo apt-get install python-pip
    
Now install humblebee using

    sudo pip install humblebee

This program also depends on `mediainfo` and `unrar` (if you want to use the unrar option). Install using

     sudo apt-get install mediainfo
     sudo apt-get install unrar
    
That's it. Now lets see how we use this thing.  

Humblebee comes with a command line interface and various options. I'll cover the basics, but too see all available options, use:
    
    humblebee --help
    
Now, lets say your TV directory is in `/home/user/TV` and that you want to present it as an organized directory of symlinks in `/home/user/cleanTV`.  
No worries, this command will not alter any of your files. Destructive options are always explicit.

    humblebee -s /home/user/TV /home/user/cleanTV
    
(note: if you want to really move your actual files (careful with this) you can simply substitute `-s` with `-r` in the above command.
    
Now humblebee starts importing your TV shows, go grab a soda, this can take a while depending on the size of your collection.
You'll notice quickly that the `cleanTV` directory is created and starts getting filled with subdirectories and symlinks within. Neat, huh?

You might also notice that in your main `TV` directory, 2 new files appear: `.humblebee.db` and `humblebee.last`. 
`.humblebee.db` contains the metadata for your TV shows. This is a normal sqlite3 database.
Paths to files in this database are all relative to your root directory (in this case `/home/user/TV`) so in case you move/rename that directory, access it through a network share, etc, the database will always point to the right files.

`.humblebee.last` is just a dictionary type file containing filenames and their last modification times. This makes the next import go much faster since humblebee doesn't bother inspecting files which haven't changed since the last run.


... More to come

## How can I help? ##
There are many ways to help. One of the most useful ways, which doesn't require any programming knowledge, is to simply use the program and report any bugs you may encounter.

You may also write useful information in the project's wiki. This helps other users get familiar with the program.

If you do have programming knowledge, feel free to send in patches and suggestions. If you make something better in any way, it will most likely be accepted.

### TODO ###
* Documentation
* Test cases
* Take over world


