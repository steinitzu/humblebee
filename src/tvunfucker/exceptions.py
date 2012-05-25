


class TVUFError(Exception):
    pass


class InvalidArgumentError(TVUFError):
    def __init__(self, *args):
        super(InvalidArgumentError, self).__init__(*args)

#fuck this
class NotADirectoryError(TVUFError):
    def __init__(self, *args):
        super(NotADirectoryError, self).__init__(*args)
