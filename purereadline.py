# This module makes GNU readline available to Python.  It has ideas
# contributed by Lee Busby, LLNL, and William Magro, Cornell Theory
# Center.  The completer interface was inspired by Lele Gaifax.  More
# recently, it was largely rewritten by Guido van Rossum.

# This is a pure Python wrapper around `readine.c` which uses `ctypes`.

from ctypes import *
import copy

# libreadline.so and libhistory.so must be on LD_LIBRARY_PATH
libreadline = cdll.LoadLibrary('libreadline.so')
libhistory = cdll.LoadLibrary('libhistory.so')


# parse_and_bind(*args)
# =====================
# The GNU readline `rl_parse_and_bind` takes <char *s>, a pointer to a string.
# Python-readline uses `PyArg_parseTuple` with the "s" formatter to check for
# <str> or <unicode> args and converts them to <char *>, then copies the pointer
# (s) and passes the copy to libreadline.
    
# Exported function to send one line to readline's init file parser

def parse_and_bind(s):
    """
    parse_and_bind(string) -> None
    Parse and execute single line of a readline init file.
    """
    # Only <str> or <unicode> input acceptable, otherwise return. If <unicode>,
    # cast as <str>. Python passes <str> as <char *> to foreign library
    # functions. -- MM 2012-12-15
    if type(s) not in [str, unicode]:
        return
    elif type(s) is unicode:
        s = str(s)
    # Make a copy -- rl_parse_and_bind() modifies its argument
    # Bernard Herzog
    s_copy = copy.copy(s) # raises copy.error exception
    libreadline.rl_parse_and_bind(s_copy)
    # s_copy garbage collected when function goes out of scope, right?


# read_init_file(*args)
# =====================
# GNU readline `rl_read_init_file` takes <char *s>, a pointer to a string which
# defaults to `NULL`. Python-readline uses `PyArg_parseTuple with the "|z"
# format to check for `None`, <str> or <unicode> args and converts `None` to
# `NULL` and <str> and <unicode> to <char *>. GNU readline `rl_read_init_file`
# returns 0 on success, non-zero <int> on fail.

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


# Python-readline `set_hook` takes a pointer to a string (*funcname), a pointer
# to a pointer to a Python object (**hook_var) and a pointer to another Python
# object (*args). It uses PyArg_parseTuple with a "|O" formatter to pass the
# (*args) as a PyObject pointer into (&function). It uses the string (funcname)
# to generate the formater, which it stores in a character array (buf), which is
# 80 bytes long, using the function `PyOS_snprintf`. The default value of
# (functon) is `None`.

# Generic hook function setter

def set_hook(function=None, hook_var):
    if function is None:
        hook_var = None
    elif hasattr(function, '__call__'):
        hook_var = function
    else:
        raise TypeError('object is not callable')


# Exported functions to specify hook functions in Python

completion_display_matches_hook = None
startup_hook = None
pre_input_hook = None


def set_completion_display_matches_hook(result):
    """
    set_completion_display_matches_hook([function]) -> None
    Set or remove the completion display function.
    The function is called as
    function(substitution, [matches], longest_match_length)
    once each time matches need to be displayed.
    """

    result = set_hook(completion_display_matches_hook)
    # We cannot set this hook globally, since it replaces the
    #  default completion display.
    if libreadline.rl_completion_display_matches_hook = completion_display_matches_hook:
        # TODO: this needs some work!
        #(libreadline.rl_compdisp_func_t *)on_completion_display_matches_hook
    elif
        0
    return result

