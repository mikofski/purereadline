# This module makes GNU readline available to Python.  It has ideas
# contributed by Lee Busby, LLNL, and William Magro, Cornell Theory
# Center.  The completer interface was inspired by Lele Gaifax.  More
# recently, it was largely rewritten by Guido van Rossum.

# This is a pure Python wrapper around `readine.c` which uses `ctypes`.

from ctypes import *

# libreadline.so and libhistory.so must be on LD_LIBRARY_PATH
libreadline = cdll.LoadLibrary('libreadline.so')
libhistory = cdll.LoadLibrary('libhistory.so')

# GNU readline defines a number of new object types that are function pointers.
# We need to redefine them in Python.
RL_COMPDISP_FUNC_T = CFUNCTYPE(c_void_p, POINTER(c_char_p), c_int, c_int)

# GNU readline variables:
rl_completion_display_matches_hook = RL_COMPDISP_FUNC_T.in_dll(libreadline,
    "rl_completion_display_matches_hook")

# GNU readline functions: specify required argument and return types
rl_parse_and_bind = libreadline.rl_parse_and_bind
rl_parse_and_bind.argtypes = [c_char_p] # mutable
rl_parse_and_bind.restype = c_int
rl_read_init_file = libreadline.rl_read_init_file
rl_read_init_file.argtypes = [c_char_p] # constant
rl_read_init_file.restype = c_int
read_history = libhistory.read_history
read_history.argtypes = [c_char_p] # constant
read_history.restype = c_int
write_history = libhistory.write_history
write_history.argtypes = [c_char_p] # constant
write_history.restype = c_int
history_truncate_file = libreadline.history_truncate_file
history_truncate_file.argtypes = [c_char_p, c_int] # string is constant
history_truncate_file.restype = c_int


# parse_and_bind(PyObject *self, PyObject *args)
# ==============================================
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
    # cast as <str>. Python string is immutable, so use `create_string_buffer()`
    # which points to mutable memory, and pass it to libreadline instead.
    if type(s) not in [str, unicode]:
        return
    elif type(s) is unicode:
        s = str(s)
    # Make a copy -- rl_parse_and_bind() modifies its argument
    # Bernard Herzog
    s_copy = create_string_buffer(s) # raises TypeError exception
    rl_parse_and_bind(s_copy)
    del(s_copy)


# read_init_file(PyObject *self, PyObject *args)
# ==============================================
# Python-readline uses `PyArg_parseTuple with the "|z" format to check for
# `None`, <str> or <unicode> args and converts `None` to `NULL` and <str> and
# <unicode> to <char *>. GNU readline `rl_read_init_file` returns 0 on success,
# non-zero <int> on fail.

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
    errno = rl_read_init_file(s)
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
    errno = read_history(s)
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
    errno = write_history(s)
    if not errno and _history_length >= 0:
        history_truncate_file(s, _history_length)
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

# set_hook(const char *funcname, PyObject **hook_var, PyObject *args)
# ===================================================================
# Python-readline uses PyArg_parseTuple with a "|O" formatter to check for a
# PyObject pointer which may be Py_None.

# Generic hook function setter

def set_hook(function=None, hook_var):
    # if function is `None`, set hook_var to `None`, otherwise set hook_var to
    # function or raise exception if function is not callable.
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


def set_completion_display_matches_hook(function=None):
    """
    set_completion_display_matches_hook([function]) -> None
    Set or remove the completion display function.
    The function is called as
    function(substitution, [matches], longest_match_length)
    once each time matches need to be displayed.
    """

    result = set_hook(function,completion_display_matches_hook)
    # We cannot set this hook globally, since it replaces the
    #  default completion display.
    if completion_display_matches_hook:
        (rl_completion_display_matches_hook
            = RL_COMPDISP_FUNC_T(on_completion_display_matches_hook)
    elif
        rl_completion_display_matches_hook = 0
    return result

