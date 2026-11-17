"""Suggest per-pot endpoint bounds from stationary low/high diagnostic CSV logs.

Desktop only; never writes firmware or claims that a capture is physical evidence.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

CONTROLS = {'A0': 'deck_a', 'A1': 'deck_b', 'A2': 'crossfader'}
COLUMNS = ['control', 'min', 'max', 'mean', 'span']


def read_capture(path):
    """Require complete windows, strict columns and internally consistent values."""
    data = path.read_bytes()
    lines = [line for line in data.decode('utf-8-sig').splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    reader = csv.DictReader(io.StringIO('\n'.join(lines)), strict=True)
    if reader.fieldnames != COLUMNS:
        raise ValueError('{}: expected CSV header {}'.format(path, ','.join(COLUMNS)))
    windows = {name: [] for name in CONTROLS}
    expected_order = tuple(CONTROLS)
    count = 0
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('{}: truncated or extra CSV columns'.format(path))
        name = row['control']
        if name != expected_order[count % 3]:
            raise ValueError('{}: expected complete A0,A1,A2 windows in order'.format(path))
        try:
            low, high, span = (int(row[key]) for key in ('min', 'max', 'span'))
            mean = float(row['mean'])
        except ValueError as error:
            raise ValueError('{}: invalid numeric value'.format(path)) from error
        if not (0 <= low <= high <= 65535 and span == high - low and
                math.isfinite(mean) and low <= mean <= high):
            raise ValueError('{}: inconsistent ADC statistics'.format(path))
        windows[name].append((low, high))
        count += 1
    if count % 3 or count < 6:
        raise ValueError('{}: capture at least two complete stationary windows'.format(path))
    return windows, hashlib.sha256(data).hexdigest()


def summarize(low_path, high_path):
    low, low_hash = read_capture(low_path)
    high, high_hash = read_capture(high_path)
    bounds = {}
    for name, key in CONTROLS.items():
        lower = max(pair[1] for pair in low[name])
        upper = min(pair[0] for pair in high[name])
        if lower >= upper:
            raise ValueError('{}: stop ranges overlap or are reversed; inspect capture/wiring'.format(name))
        bounds[key] = {'pin': name, 'minimum': lower, 'maximum': upper,
                       'usable_raw_span': upper - lower,
                       'low_windows': len(low[name]), 'high_windows': len(high[name]),
                       'largest_low_window_span': max(b - a for a, b in low[name]),
                       'largest_high_window_span': max(b - a for a, b in high[name])}
    return {'status': 'candidate_bounds_only', 'firmware_modified': False,
            'physical_validation': 'not established by this tool',
            'inputs': {'low': {'path': str(low_path), 'sha256': low_hash},
                       'high': {'path': str(high_path), 'sha256': high_hash}},
            'candidate_bounds': bounds}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--low', type=Path, required=True)
    parser.add_argument('--high', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = summarize(args.low, args.high)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        parser.exit(2, 'Calibration capture rejected: {}\n'.format(error))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
