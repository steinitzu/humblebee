from time import mktime


def zero_prefix_int(num):
    """
    zero_prefix_number(int) -> str\n
    Puts a zero in fron of 1 digit numbers.\n
    otherwise just returns the int
    """
    strnum = str(num)
    if len(strnum) == 1:
        return '0'+strnum
    return num

def timestamp(dt):
    return mktime(dt.timetuple())
