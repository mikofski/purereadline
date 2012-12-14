# This module makes GNU readline available to Python.  It has ideas
# contributed by Lee Busby, LLNL, and William Magro, Cornell Theory
# Center.  The completer interface was inspired by Lele Gaifax.  More
# recently, it was largely rewritten by Guido van Rossum.

from ctypes import *
import copy

# libreadline.so and libhistory.so must be on LD_LIBRARY_PATH
libreadline = cdll.LoadLibrary('libreadline.so')
libhistory = cdll.LoadLibrary('libhistory.so')


# parse_and_bind(*args)
# =====================
# 1. PyArg_parseTuple with format: "s" converts python string or Unicode object
#   to char * -- check args are string or Unicode and convert Unicode to string
# 2. don't catch copy error, since it raises copy.error exception
# 3. don't recast s to c_char_p since Python pass strings as char *
# 4. Python garbage collects s_copy as soon as it goes out of scope
    
# Exported function to send one line to readline's init file parser

def parse_and_bind(s):
    """
    parse_and_bind(string) -> None
    Parse and execute single line of a readline init file.
    """ 
    if type(s) not in [str, unicode]:
        return
    elif type(s) is unicode:
        s = str(s)
    # Make a copy -- rl_parse_and_bind() modifies its argument
    # Bernard Herzog
    s_copy = copy.copy(s)
    libreadline.rl_parse_and_bind(s_copy)


# read_init_file(*args)
# =====================
# 1. PyArg_ParseTuple with format: "|z" converts python string, Unicode or None
#   to char * or NULL -- check args and convert Unicode to string
# 2. rl_read_init_file returns 0 on success, non-zero int on fail

# Exported function to parse a readline init file

def read_init_file(s=None):
    """
    read_init_file([filename]) -> None
    Parse a readline initialization file.
    The default filename is the last filename used.
    """
    if s is not None and type(s) not in [str, unicode]:
        return
    elif type(s) is unicode:
        s = str(s)
    errno = libreadline.rl_read_init_file(s)
    if errno:
        raise IOError(2,'No such file or directory',s)


# Exported function to load a readline history file

def read_history_file(s=None):
    """
    read_history_file([filename]) -> None
    Load a readline history file.
    The default filename is ~/.history.
    """
    if s is not None and type(s) not in [str, unicode]:
        return
    elif type(s) is unicode:
        s = str(s)
    errno = libreadline.read_history(s)
    if errno:
        raise IOError(2,'No such file or directory',s)


_history_length = -1 # do not truncate history by default


# Exported function to save a readline history file

def write_history_file(s=None):
    """
    write_history_file([filename]) -> None
    Save a readline history file.
    The default filename is ~/.history.
    """
    if s is not None and type(s) not in [str, unicode]:
        return
    elif type(s) is unicode:
        s = str(s)
    errno = libreadline.write_history(s)
    if not errno and _history_length >= 0:
        libreadline.history_truncate_file(s, _history_length)
    if (errno)
        raise IOError(2,'No such file or directory',s)


# Set history length

def set_history_length(length=_history_length):
    """
    set_history_length(length) -> None
    set the maximal number of items which will be written to
    the history file. A negative length is used to inhibit
    history truncation.
    """
    _history_length = length


# Get history length

def get_history_length():
    """
    get_history_length() -> int
    return the maximum number of items that will be written to
    the history file.
    """
    return _history_length

# Generic hook function setter

def set_hook(function=None):
    pass

