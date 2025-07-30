# tests/test_baud_rate.py
import asyncio
import pytest
import serial

from pleco.__main__ import read_serial

class DummyAwaitable:
    def __await__(self):
        # yield exactly one time so that read_serial suspends at this point
        yield
        return None

def dummy_sleep(delay, *args, **kwargs):
    return DummyAwaitable()

def test_read_serial_uses_configured_baud_rate(monkeypatch):
    # 1) stub out serial.Serial as before
    captured = {}
    def dummy_serial(port, baudrate, timeout):
        captured['port'] = port
        captured['baudrate'] = baudrate
        class DummyPort:
            def readline(self):
                return b''  # no data
            def __enter__(self): return self
            def __exit__(self, *args): pass
        return DummyPort()

    monkeypatch.setattr(serial, 'Serial', dummy_serial)

    # 2) stub out asyncio.sleep to our dummy awaitable
    monkeypatch.setattr(asyncio, 'sleep', dummy_sleep)

    # 3) drive the coroutine up to its first await
    q = asyncio.Queue()
    coro = read_serial('COMX', 38400, q)
    aw = coro.__await__()
    _ = aw.send(None)   # now stops cleanly at our DummyAwaitable

    # 4) assert it actually opened the port with the right args
    assert captured['baudrate'] == 38400
    assert captured['port'] == 'COMX'
