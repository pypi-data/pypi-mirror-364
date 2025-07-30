import asyncio
import tempfile
import os
import shutil
import pytest
from unittest import mock
from pleco.__main__ import main


class FakeSerial:
    def __init__(self, *args, **kwargs):
        self.lines = [
            b"$GPGGA,22938.98,3007.11937,N,8835.0814,W,2,25,0.5,-17.2,M,,,,*34\n",
            b"$GPHDG,98.3,,,,A*2D\n",
            b"$GPRMC,22938.98,A,3007.11937,N,8835.0814,W,9.7,100.3,170523,,*2E\n",
            b"$GPVTG,100.3,T,,,9.7,N,17.9,K*1E\n",
            b"$GPDPT,100"
        ]
        self.index = 0
        self.closed = False

    def readline(self):
        if self.index < len(self.lines):
            line = self.lines[self.index]
            self.index += 1
            return line
        return b""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

@pytest.mark.asyncio
async def test_end_to_end(monkeypatch):
    # Create temp directory
    tmp_dir = tempfile.mkdtemp()
    raw_file = os.path.join(tmp_dir, "raw.csv")
    clean_file = os.path.join(tmp_dir, "clean.csv")

    # Patch CLI args
    monkeypatch.setattr("sys.argv", [
        "pleco",
        "-c", "FAKE_PORT",
        "-r", raw_file,
        "-o", clean_file,
        "-i", "1",
        "-g", "GPRMC 3", "GPHDG 1", "GPDPT 1"
    ])

    # Patch serial.Serial to return fake NMEA lines
    monkeypatch.setattr("serial.Serial", lambda *args, **kwargs: FakeSerial())

    # Start main loop, let it process a few cycles
    task = asyncio.create_task(main())
    await asyncio.sleep(5)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Check RAW.csv was written
    assert os.path.exists(raw_file)
    with open(raw_file, "r", encoding='utf-8', errors="ignore") as f:
        raw_lines = f.readlines()
    assert len(raw_lines) >= 2

    # Check CLEANED.csv exists and contains correct single-row, no-header values
    assert os.path.exists(clean_file)
    with open(clean_file, "r") as f:
        clean_lines = f.read().strip()

    # Split line to inspect actual values
    values = clean_lines.split(",")
    assert len(values) == 3  # GPRMC_3, GPHDG_1, GPDPT_1

    # These are expected values from FakeSerial's lines:
    # - GPRMC 3 = "3007.11937"
    # - GPHDG 1 = "98.3"
    # - GPDPT 1 = "100"
    assert values[0] == "3007.11937"
    assert values[1] == "98.3"
    assert values[2] == "100"

    # Cleanup
    shutil.rmtree(tmp_dir)
