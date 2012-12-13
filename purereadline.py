# This module makes GNU readline available to Python.  It has ideas
# contributed by Lee Busby, LLNL, and William Magro, Cornell Theory
# Center.  The completer interface was inspired by Lele Gaifax.  More
# recently, it was largely rewritten by Guido van Rossum.

from ctypes import *
import copy

libreadline = CDLL('libreadline.so')
libhistory = CDLL('libhistory.so')


# Exported function to send one line to readline's init file parser

def parse_and_bind(s):
 """parse_and_bind(string) -> None\n\
Parse and execute single line of a readline init file.""" 
    if type(s) not in [str, unicode]
        return None
    # Make a copy -- rl_parse_and_bind() modifies its argument
    # Bernard Herzog
    s_copy = copy.copy(s)
    c_s_copy = c_char_p(s_copy)
    libreadline.rl_parse_and_bind(c_s_copy)
    return None

 # Exported function to parse a readline init file

def read_init_file(s)
{
    char *s = NULL;
    if (!PyArg_ParseTuple(args, "|z:read_init_file", &s))
        return NULL;
    errno = rl_read_init_file(s);
    if (errno)
        return PyErr_SetFromErrno(PyExc_IOError);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(doc_read_init_file,
"read_init_file([filename]) -> None\n\
Parse a readline initialization file.\n\
The default filename is the last filename used.");