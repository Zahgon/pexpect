import os
import sys
import stat
import select
import time
import errno

try:
    InterruptedError
except NameError:
    # Alias Python2 exception to Python3
    InterruptedError = select.error

if sys.version_info[0] >= 3:
    string_types = (str,)
else:
    string_types = (unicode, str)


def is_executable_file(path):
    """Checks that path is an executable regular file, or a symlink towards one.

    This is roughly ``os.path isfile(path) and os.access(path, os.X_OK)``.
    """
    pass


def which(filename, env=None):
    '''This takes a given filename; tries to find it in the environment path;
    then checks if it is executable. This returns the full path to the filename
    if found and executable. Otherwise this returns None.'''
    pass


def split_command_line(command_line):

    '''This splits a command line into a list of arguments. It splits arguments
    on spaces, but handles embedded quotes, doublequotes, and escaped
    characters. It's impossible to do this with a regular expression, so I
    wrote a little state machine to parse the command line. '''
    pass


def select_ignore_interrupts(iwtd, owtd, ewtd, timeout=None):

    '''This is a wrapper around select.select() that ignores signals. If
    select.select raises a select.error exception and errno is an EINTR
    error then it is ignored. Mainly this is used to ignore sigwinch
    (terminal resize). '''

    # if select() is interrupted by a signal (errno==EINTR) then
    # we loop back and enter the select() again.
    if timeout is not None:
        end_time = time.time() + timeout
    while True:
        try:
            return select.select(iwtd, owtd, ewtd, timeout)
        except InterruptedError:
            err = sys.exc_info()[1]
            if err.args[0] == errno.EINTR:
                # if we loop back we have to subtract the
                # amount of time we already waited.
                if timeout is not None:
                    timeout = end_time - time.time()
                    if timeout < 0:
                        return([], [], [])
            else:
                # something else caused the select.error, so
                # this actually is an exception.
                raise


def poll_ignore_interrupts(fds, timeout=None):
    '''Simple wrapper around poll to register file descriptors and
    ignore signals.'''

    if timeout is not None:
        end_time = time.time() + timeout

    poller = select.poll()
    for fd in fds:
        poller.register(fd, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)

    while True:
        try:
            timeout_ms = None if timeout is None else timeout * 1000
            results = poller.poll(timeout_ms)
            return [afd for afd, _ in results]
        except InterruptedError:
            err = sys.exc_info()[1]
            if err.args[0] == errno.EINTR:
                # if we loop back we have to subtract the
                # amount of time we already waited.
                if timeout is not None:
                    timeout = end_time - time.time()
                    if timeout < 0:
                        return []
            else:
                # something else caused the select.error, so
                # this actually is an exception.
                raise
