import asyncio
import os
import tempfile
import pytest
from unittest import mock
from pleco.__main__ import read_serial, save_raw_log


class FakeSerial:
    def __init__(self, *args, **kwargs):
        self.lines = [
            b"$GPRMC,ignore1,ignore2,DATA1\n",
            b"$GPHDG,DATA_HEADING\n"
        ]
        self.index = 0
        self.closed = False

    def readline(self):
        if self.index < len(self.lines):
            line = self.lines[self.index]
            self.index += 1
            return line
        return b""

    def __enter__(self): return self
    def __exit__(self, *args): self.closed = True


@pytest.mark.asyncio
async def test_raw_log_writing(monkeypatch):
    # Set up temp raw file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        raw_path = tmp_file.name

    # Patch serial.Serial to return fake data
    monkeypatch.setattr("serial.Serial", lambda *args, **kwargs: FakeSerial())

    # Shared queue between read and write
    data_queue = asyncio.Queue()

    # Start read/write tasks
    read_task = asyncio.create_task(read_serial("FAKE_PORT",9600, data_queue))
    save_task = asyncio.create_task(save_raw_log(raw_path, data_queue))

    await asyncio.sleep(1.5)  # Allow time to read/write

    # Cleanly cancel tasks
    read_task.cancel()
    save_task.cancel()
    await asyncio.gather(read_task, save_task, return_exceptions=True)

    # Verify raw file contents
    with open(raw_path, "rb") as f:
        contents = f.read().decode(errors="ignore")
        assert "$GPRMC" in contents
        assert "$GPHDG" in contents

    os.unlink(raw_path)
