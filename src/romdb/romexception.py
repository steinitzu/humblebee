#!/usr/bin/env python
#encoding:utf-8


class RomError(Exception):
    pass

class FileNotFoundError(RomError):
    def __init__(self, *args):
        super(FileNotFoundError, self).__init__(*args)

class InvalidArgumentError(RomError):
    def __init__(self, *args):
        super(InvalidArgumentError, self).__init__(*args)

def main():
    raise FileNotFoundError('lol', 'ae2')

if __name__ == '__main__':
    main()
