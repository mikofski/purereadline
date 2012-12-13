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

def read_init_file(s):
    """
    read_init_file([filename]) -> None
    Parse a readline initialization file.
    The default filename is the last filename used.
    """
    if type(s) not in [str, unicode, None]:
        return
    elif type(s) is unicode:
        s = str(s)
    errno = libreadline.rl_read_init_file(s);
    if errno:
        raise IOError(2,'No such file or directory',s)
