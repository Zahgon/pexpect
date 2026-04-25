"""Implementation of coroutines without using ``async def``/``await`` keywords.

``@asyncio.coroutine`` and ``yield from`` are  used here instead.
"""
import asyncio
import errno
import signal

from pexpect import EOF


@asyncio.coroutine
def expect_async(expecter, timeout=None):
    # First process data that was previously read - if it maches, we don't need
    # async stuff.
    idx = expecter.existing_data()
    if idx is not None:
        return idx
    if not expecter.spawn.async_pw_transport:
        pw = PatternWaiter()
        pw.set_expecter(expecter)
        transport, pw = yield from asyncio.get_event_loop().connect_read_pipe(
            lambda: pw, expecter.spawn
        )
        expecter.spawn.async_pw_transport = pw, transport
    else:
        pw, transport = expecter.spawn.async_pw_transport
        pw.set_expecter(expecter)
        transport.resume_reading()
    try:
        return (yield from asyncio.wait_for(pw.fut, timeout))
    except asyncio.TimeoutError as e:
        transport.pause_reading()
        return expecter.timeout(e)


@asyncio.coroutine
def repl_run_command_async(repl, cmdlines, timeout=-1):
    pass


class PatternWaiter(asyncio.Protocol):
    transport = None

    def set_expecter(self, expecter):
        self.expecter = expecter
        self.fut = asyncio.Future()

    def found(self, result):
        pass

    def error(self, exc):
        pass

    def connection_made(self, transport):
        pass

    def data_received(self, data):
        pass

    def eof_received(self):
        # N.B. If this gets called, async will close the pipe (the spawn object)
        # for us
        pass

    def connection_lost(self, exc):
        pass
