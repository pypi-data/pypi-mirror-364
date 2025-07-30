# tests/test_cli_entry.py
import subprocess
import sys
from pathlib import Path


def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "pleco", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "Read and clean ROV serial data" in result.stdout
