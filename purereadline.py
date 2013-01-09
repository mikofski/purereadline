# This module makes GNU readline available to Python.  It has ideas
# contributed by Lee Busby, LLNL, and William Magro, Cornell Theory
# Center.  The completer interface was inspired by Lele Gaifax.  More
# recently, it was largely rewritten by Guido van Rossum.

# This is a pure Python wrapper around GNU libreadline using `ctypes`, adapted
# from python-readline.

# References:
# ===========
# http://cnswww.cns.cwru.edu/php/chet/readline/rltop.html
# http://cnswww.cns.cwru.edu/php/chet/readline/readline.html
# http://cnswww.cns.cwru.edu/php/chet/readline/history.html
# http://pypi.python.org/pypi/readline

from ctypes import *

# libreadline.so and libhistory.so must be on LD_LIBRARY_PATH
libreadline = cdll.LoadLibrary('libreadline.so')
libhistory = cdll.LoadLibrary('libhistory.so')

# GNU readline defines new object types that are function pointers. We need to
# redefine them in Python.
RL_COMPDISP_FUNC_T = CFUNCTYPE(None, POINTER(c_char_p), c_int, c_int)
RL_COMPENTRY_FUNC_T = CFUNCTYPE(c_char_p, c_char_p, c_int)
RL_HOOK_FUNC_T = CFUNCTYPE(c_int)

# GNU readline variables:
rl_completion_display_matches_hook = POINTER(RL_COMPDISP_FUNC_T).in_dll(
    libreadline, "rl_completion_display_matches_hook")
rl_pre_input_hook = POINTER(RL_HOOK_FUNC_T).in_dll(libreadline,
    "rl_pre_input_hook")
rl_completion_type = c_int.in_dll(libreadline, "rl_completion_type")
rl_completer_word_break_characters = c_char_p.in_dll(libreadline,
    "rl_completer_word_break_characters")
rl_line_buffer = c_char_p.in_dll(libreadline, "rl_line_buffer")
rl_attempted_completion_over = c_int.in_dll(libreadline,
    "rl_attempted_completion_over")
rl_completion_append_character = c_int.in_dll(libreadline,
    "rl_completion_append_character")
rl_completion_suppress_append = c_int.in_dll(libreadline,
    "rl_completion_suppress_append")

# GNU readline functions: specify required argument and return types
rl_completion_matches = libreadline.rl_completion_matches
rl_completion_matches.argtypes = [c_char_p, POINTER(RL_COMPENTRY_FUNC_T)]
rl_completion_matches.restype = POINTER(c_char_p)
rl_parse_and_bind = libreadline.rl_parse_and_bind
rl_parse_and_bind.argtypes = [c_char_p] # mutable
rl_parse_and_bind.restype = c_int
rl_read_init_file = libreadline.rl_read_init_file
rl_read_init_file.argtypes = [c_char_p] # constant
rl_read_init_file.restype = c_int
rl_insert_text = libreadline.rl_insert_text
rl_insert_text.argtypes = [c_char_p]
rl_insert_text.restype = c_int
rl_redisplay = libreadline.rl_redisplay
rl_redisplay.argtypes = []
rl_redisplay.restype = None
read_history = libhistory.read_history
read_history.argtypes = [c_char_p] # constant
read_history.restype = c_int
write_history = libhistory.write_history
write_history.argtypes = [c_char_p] # constant
write_history.restype = c_int
history_truncate_file = libreadline.history_truncate_file
history_truncate_file.argtypes = [c_char_p, c_int] # string is constant
history_truncate_file.restype = c_int
free_history_entry = libhistory.free_history_entry
free_history_entry.argtypes = [POINTER(HIST_ENTRY)]
free_history_entry.restype = histdata_t
remove_history = libhistory.remove_history
remove_history.argtypes = [c_int]
remove_history.restype = POINTER(HIST_ENTRY)
replace_history_entry = libhistory.replace_history_entry
replace_history_entry.argtypes = [c_int, c_char_p, histdata_t]
replace_history_entry.restype = POINTER(HIST_ENTRY)
add_history = libhistory.add_history
add_history.argtypes = [c_char_p]
add_history.restype = None
history_get_history_state = libhistory.history_get_history_state
history_get_history_state.argtypes = []
history_get_history_state.restype = POINTER(HISTORY_STATE)
history_get = libhistory.history_get
history_get.argtypes = [c_int]
history_get.restype = POINTER(HIST_ENTRY)
clear_history = libhistory.clear_history
clear_history.argtypes = []
clear_history.restype = None


# GNU readline structures:
histdata_t = c_void_p


class HIST_ENTRY(Structure):
    _fields_ = [("line", c_char_p),
                ("timestamp", c_char_p),
                ("data", histdata_t)]


# A structure used to pass around the current state of the history.

class HISTORY_STATE(Structure):
    # Pointer to the entries themselves.
    _fields_ = [("entries", POINTER(POINTER(HIST_ENTRY)),
                ("offset", c_int), # The location pointer within this array.
                ("length", c_int), # Number of elements within this array.
                ("size", c_int),  # Number of slots allocated to this array.
                ("flags", c_int)]


def completion_matches(text, entry_func):
    return rl_completion_matches(text, POINTER(RL_COMPENTRY_FUNC_T(entry_func)))


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
    elif type(s) == unicode:
        s = str(s)
    # Make a copy -- rl_parse_and_bind() modifies its argument
    # Bernard Herzog
    s_copy = create_string_buffer(s) # raises TypeError exception
    rl_parse_and_bind(s_copy)


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
    if s != None and type(s) not in [str, unicode]:
        return
    elif type(s) == unicode:
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
    if s != None and type(s) not in [str, unicode]:
        return
    elif type(s) == unicode:
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
    if s != None and type(s) not in [str, unicode]:
        return
    elif type(s) == unicode:
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
    if function == None:
        hook_var.contents.value = None
    elif hasattr(function, '__call__'):
        hook_var.contents.value = function
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
    # TODO: use CFUNTYPE to define function types instead of using generic
    # "Python object" type.
    result = set_hook(function,
        pointer(py_object(completion_display_matches_hook)))
    # We cannot set this hook globally, since it replaces the
    #  default completion display.
    if completion_display_matches_hook:
        (rl_completion_display_matches_hook
            = POINTER(RL_COMPDISP_FUNC_T(on_completion_display_matches_hook)))
    elif
        rl_completion_display_matches_hook = 0
    return result


def set_startup_hook(function=None):
    """
    set_startup_hook([function]) -> None
    Set or remove the startup_hook function.
    The function is called with no arguments just
    before readline prints the first prompt.
    """
    # TODO: use CFUNTYPE to define function types instead of using generic
    # "Python object" type.
    return set_hook(function, pointer(py_object(startup_hook)))


def set_pre_input_hook(function=None):
    """
    set_pre_input_hook([function]) -> None
    Set or remove the pre_input_hook function.
    The function is called with no arguments after the first prompt
    has been printed and just before readline starts reading input
    characters.
    """
    # TODO: use CFUNTYPE to define function types instead of using generic
    # "Python object" type.
    return set_hook(function, pointer(py_object(pre_input_hook)))


# Exported function to specify a word completer in Python

completer = None
begidx = None
endidx = None


# Get the completion type for the scope of the tab-completion
def get_completion_type():
    """
    get_completion_type() -> int
    Get the type of completion being attempted.
    """
    return rl_completion_type


# Get the beginning index for the scope of the tab-completion

def get_begidx():
    """
    get_begidx() -> int
    get the beginning index of the readline tab-completion scope
    """
    return begidx


# Get the ending index for the scope of the tab-completion

def get_endidx():
    """
    get_endidx() -> int
    get the ending index of the readline tab-completion scope
    """
    return endidx


# Set the tab-completion word-delimiters that readline uses

def set_completer_delims(break_chars):
    """
    set_completer_delims(string) -> None
    set the readline word delimiters for tab-completion
    """
    if type(break_chars) not in [str, unicode]:
        return
    elif type(break_chars) == unicode:
        break_chars = str(break_chars)
    # Not going to `free` malloc'd memory. Future Python strings will garbage
    # collect themselves. `create_string_buffer` not necessary.
    rl_completer_word_break_characters.value = break_chars


# _py_free_history_entry: Utility function to free a history entry.

# Readline version >= 5.0 introduced a timestamp field into the history entry
# structure; this needs to be freed to avoid a memory leak.  This version of
# readline also introduced the handy 'free_history_entry' function, which
# takes care of the timestamp.

def _py_free_history_entry(entry):
    data = free_history_entry(entry)
    # Not going to free data.


def py_remove_history(entry_number):
    """
    remove_history_item(pos) -> None
    remove history item given by its position
    """
    if type(entry_number) != int:
        return
    elif entry_number < 0:
        raise ValueError("History index cannot be negative")
    entry = remove_history(entry_number)
    if (!entry):
        raise ValueError("No history item at position %d" % entry_number)
    # free memory allocated for the history entry
    _py_free_history_entry(entry)


def py_replace_history(entry_number, line):
    """
    replace_history_item(pos, line) -> None
    replaces history item given by its position with contents of line
    """
    if type(entry_number) != int or type(line) not in [str, unicode]:
        return
    elif entry_number < 0:
        raise ValueError("History index cannot be negative")
    old_entry = replace_history_entry(entry_number, line, c_void_p(None))
    if (!old_entry):
        raise ValueError("No history item at position %d" % entry_number)
    # free memory allocated for the history entry
    _py_free_history_entry(old_entry)


# Add a line to the history buffer

def py_add_history(line):
    """
    add_history(string) -> None
    add a line to the history buffer
    """
    if type(line) not in [str, unicode]:
        return
    elif type(line) == unicode:
        line = str(line)
    add_history(line)


# Get the tab-completion word-delimiters that readline uses

def get_completer_delims():
    """
    get_completer_delims() -> string
    get the readline word delimiters for tab-completion
    """
    return rl_completer_word_break_characters.value


# Set the completer function

def set_completer(function=None):
    """
    set_completer([function]) -> None
    Set or remove the completer function.
    The function is called as function(text, state),
    for state in 0, 1, 2, ..., until it returns a non-string.
    It should return the next possible completion starting with 'text'.
    """
    return set_hook(function, pointer(py_object(completer)))


def get_completer():
    """
    get_completer() -> function
    Returns current completer function.
    """
    return completer

# Private function to get current length of history.  XXX It may be
# possible to replace this with a direct use of history_length instead,
# but it's not clear whether BSD's libedit keeps history_length up to date.
# See issue #8065.

def _py_get_history_length():
    hist_st = history_get_history_state()
    length = hist_st.length
    # the history docs don't say so, but the address of hist_st changes each
    # time history_get_history_state is called which makes me think it's
    # freshly malloc'd memory...  on the other hand, the address of the last
    # line stays the same as long as history isn't extended, so it appears to
    # be malloc'd but managed by the history package... */
    # Not going to free hist_st, should be garbage collected by Python
    return length;


# Exported function to get any element of history

def get_history_item(idx=0):
    """
    get_history_item() -> string
    return the current contents of history item at index.
    """
    if type(idx) != int:
        return
    hist_ent = history_get(idx)
    if hist_ent:
        return hist_ent.line


# Exported function to get current length of history

def get_current_history_length():
    """
    get_current_history_length() -> integer
    return the current (not the maximum) length of history.
    """
    return _py_get_history_length()


# Exported function to read the current line buffer

def get_line_buffer():
    """
    get_line_buffer() -> string
    return the current contents of the line buffer.
    """
    return rl_line_buffer


# Exported function to clear the current history

def py_clear_history():
    """
    clear_history() -> None
    Clear the current readline history.
    """
    clear_history()


# Exported function to insert text into the line buffer

def insert_text(s):
    """
    insert_text(string) -> None
    Insert text into the command line.
    """
    if type(s) not in [str, unicode]:
        return
    elif type(s) == unicode:
        s = str(s)
    rl_insert_text(s)


# Redisplay the line buffer

def redisplay():
    """
    redisplay() -> None
    Change what's displayed on the screen to reflect the current
    contents of the line buffer.
    """
    rl_redisplay()


# C function to call the Python hooks.

def on_hook(func):
    # python-readline uses PyObject_CallFunction, which returns NULL on failure
    result = int(0)
    if func != None:
        r = func()
        if r != None:
            result = int(r)
    return result


def on_startup_hook():
    return on_hook(startup_hook)


def on_pre_input_hook():
    return on_hook(pre_input_hook)


# C function to call the Python completion_display_matches

def on_completion_display_matches_hook(matches, num_matches, max_length):
    m = []
    for i in range(num_matches - 1):
        s = str(matches[i + 1])
        m.append(s)
    r = completion_display_matches_hook(matches[0], m, max_length)


# C function to call the Python completer.

def on_completion(text, state):
    result = None
    if completer != None:
        rl_attempted_completion_over = 1
        r = completer(text, state)
        if r != None:
            s = str(r)
            result = create_string_buffer(s)
    return result


# A more flexible constructor that saves the "begidx" and "endidx"
# before calling the normal completer

def flex_complete(text, start, end):
    rl_completion_append_character = None
    rl_completion_suppress_append = 0
    begidx = start
    endidx = end
    return completion_matches(text, on_completion);


