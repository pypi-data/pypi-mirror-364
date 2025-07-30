import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest import mock
from pleco.__main__ import (
    is_new_data_available,
    clean_raw_log,
    save_raw_log,
)


def test_is_new_data_available(tmp_path):
    file = tmp_path / "RAW.csv"

    # Test when file does not exist
    assert is_new_data_available(str(file)) is False

    # Test with 1 line (header only)
    file.write_text("Header\n")
    assert is_new_data_available(str(file)) is False

    # Test with 2+ lines
    file.write_text("Header\nData1\n")
    assert is_new_data_available(str(file)) is True


@pytest.mark.asyncio
async def test_save_raw_log(tmp_path):
    file = tmp_path / "RAW.csv"
    queue = asyncio.Queue()
    test_line = b"$GPRMC,123,data\n"

    await queue.put(test_line)
    task = asyncio.create_task(save_raw_log(str(file), queue))

    # Give the async loop a chance to write the file
    await asyncio.sleep(0.2)
    task.cancel()

    contents = file.read_bytes()
    assert test_line in contents


@pytest.mark.asyncio
async def test_clean_raw_log(tmp_path):
    raw_file = tmp_path / "RAW.csv"
    clean_file = tmp_path / "CLEANED.csv"

    # Create a fake RAW file with multiple rows
    raw_data = "\n".join([
        "$GPRMC,ignore1,ignore2,DATA3",
        "$GPDPT,ignore1,DATA2",
        "$GPRMC,ignore1,ignore2,DATA3_B"  # most recent GPRMC 3
    ])
    raw_file.write_text(raw_data)

    # Call cleaner with two NMEA fields
    await clean_raw_log(str(raw_file), str(clean_file), ["GPRMC 3", "GPDPT 2"])

    # Ensure file exists
    assert clean_file.exists()

    # Read result and assert it's a single row, no header, latest values
    text = clean_file.read_text().strip()
    values = text.split(',')

    # There should be exactly 2 columns (one for each sentence-column pair)
    assert len(values) == 2

    # Expect latest GPRMC 3 value ("DATA3_B") and latest GPDPT 2 ("DATA2")
    assert values[0] == "DATA3_B"
    assert values[1] == "DATA2"
