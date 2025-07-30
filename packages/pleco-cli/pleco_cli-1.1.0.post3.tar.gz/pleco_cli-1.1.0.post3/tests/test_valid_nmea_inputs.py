# tests/test_args_validation.py
import sys
import pytest
from pleco.__main__ import validate_nmea_sentences

@pytest.mark.asyncio
async def test_valid_nmea_inputs():
    valid = ["GPRMC 3", "GPVTG 2", "GPGGA 100"]
    # Should not raise
    validate_nmea_sentences(valid)
@pytest.mark.asyncio
async def test_invalid_nmea_inputs(monkeypatch):
    invalid_cases = [
        ["gprmc 3"],        # lowercase
        ["GPRMC three"],    # word not number
        ["GP 3"],           # too short
        ["GPRMC"],          # missing column
        ["GPRMC 0"],        # out of range
        ["GPRMC 101"],      # out of range
        ["GPRMC -1"],       # negative
        ["GPRMC3"],         # missing space
    ]
    for case in invalid_cases:
        with pytest.raises(SystemExit) as excinfo:
            validate_nmea_sentences(case)
        assert excinfo.value.code == 1
