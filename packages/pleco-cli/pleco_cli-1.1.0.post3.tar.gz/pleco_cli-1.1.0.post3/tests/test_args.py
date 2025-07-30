# tests/test_args.py
import sys
import pytest
from pleco.__main__ import parse_args


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['pleco'])
    args = parse_args()
    assert args.com_port == 'COM3'
    assert args.raw_output_path == 'RAW.csv'
    assert args.cleaned_output_path == 'CLEANED.csv'
    assert args.clean_interval == 1
    assert args.gpnmea == ["GPDPT 1", "GPRMC 3", "GPRMC 5"]


def test_parse_args_custom(monkeypatch):
    monkeypatch.setattr(sys, 'argv', [
        'pleco', '-c', 'COM5', '-r', 'raw.csv', '-o', 'clean.csv', '-i', '10', '-g', 'GPGGA 2', 'GPVTG 5'
    ])
    args = parse_args()
    assert args.com_port == 'COM5'
    assert args.raw_output_path == 'raw.csv'
    assert args.cleaned_output_path == 'clean.csv'
    assert args.clean_interval == 10
    assert args.gpnmea == ['GPGGA 2', 'GPVTG 5']
