import pytest
import asyncio
from pathlib import Path
from pleco.__main__ import clean_raw_log

@pytest.mark.asyncio
async def test_clean_raw_log_skips_empty_and_fallback(tmp_path):
    # Prepare raw and cleaned file paths
    raw_file = tmp_path / "RAW.csv"
    clean_file = tmp_path / "CLEANED.csv"

    # RAW.csv contains some empty fields that should be skipped
    lines = [
        "$GPRMC,foo,bar,val1",
        "$GPRMC,foo,bar,",          # empty field, should fallback to val1 until a non-empty is found
        "$GPRMC,foo,bar,val3",     # latest non-empty for GPRMC column 3
        "$GPDPT,foo,val2a",        # latest non-empty for GPDPT column 2
        "$GPDPT,foo,"               # empty, should fallback to val2a
    ]
    raw_file.write_text("\n".join(lines))

    # Run cleaner
    await clean_raw_log(str(raw_file), str(clean_file), ["GPRMC 3", "GPDPT 2"])

    # Expect one-row CSV with val3 for GPRMC_3 and val2a for GPDPT_2
    content = clean_file.read_text().strip()
    assert content == "val3,val2a"

@pytest.mark.asyncio
async def test_clean_raw_log_all_empty_and_missing(tmp_path):
    raw_file = tmp_path / "RAW.csv"
    clean_file = tmp_path / "CLEANED.csv"

    # RAW.csv has only empty or missing lines for requested sentences
    lines = [
        "$GPRMC,foo,bar,",   # empty field
        "$GPRMC,foo,bar,",   # empty again
        "$GPXXX,foo,bar,baz" # valid for GPXXX column 3
    ]
    raw_file.write_text("\n".join(lines))

    # Use GPRMC 3 (all empty) and GPXXX 3 (one non-empty -> baz)
    await clean_raw_log(str(raw_file), str(clean_file), ["GPRMC 3", "GPXXX 3"])

    # First column should be empty, second 'baz'
    content = clean_file.read_text().strip()
    assert content == ",baz"

@pytest.mark.asyncio
async def test_clean_raw_log_overwrites_existing(tmp_path):
    raw_file = tmp_path / "RAW.csv"
    clean_file = tmp_path / "CLEANED.csv"

    # Existing CLEANED.csv content
    clean_file.write_text("oldcontent\n")

    # RAW.csv has one valid line
    raw_file.write_text("$GPRMC,foo,bar,valX")

    # Clean with single field
    await clean_raw_log(str(raw_file), str(clean_file), ["GPRMC 3"])

    # CLEANED.csv should now only contain the new single value, not the oldcontent
    content = clean_file.read_text().strip()
    assert content == "valX"

@pytest.mark.asyncio
async def test_clean_raw_log_one_column(tmp_path):
    raw_file = tmp_path / "RAW.csv"
    clean_file = tmp_path / "CLEANED.csv"

    # Multiple lines for one sentence
    raw_file.write_text("\n".join([
        "$GPVTG,1,2,3,4,5,6,7,8,9,10",  # column 5 = 5
        "$GPVTG,1,2,3,4,,6,7,8,9,10",    # empty column 5, fallback=5
        "$GPVTG,1,2,3,4,11,6,7,8,9,10"   # column 5 = 11
    ]))

    # Only GPVTG 5
    await clean_raw_log(str(raw_file), str(clean_file), ["GPVTG 5"])

    # Should pick 11
    content = clean_file.read_text().strip()
    assert content == "11"
