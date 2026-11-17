"""Synthetic fixtures only: these are not prototype measurements."""
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import sys
import json
import unittest

path = Path(__file__).resolve().parents[1] / 'tools/summarize_calibration.py'
spec = importlib.util.spec_from_file_location('summarize_calibration', path)
calibration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calibration)


class CalibrationCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.low = Path(self.temp.name) / 'low.csv'
        self.high = Path(self.temp.name) / 'high.csv'

    def capture(self, path, base):
        rows = ['# Synthetic test fixture', 'control,min,max,mean,span']
        for offset in (0, 1):
            for i, name in enumerate(('A0', 'A1', 'A2')):
                value = base + i * 100 + offset
                rows.append('{},{},{},{},2'.format(name, value, value + 2, value + 1))
            rows.append('# Raw switch levels: ignored snapshot')
        path.write_text('\n'.join(rows) + '\n')

    def test_suggests_independent_inner_bounds_and_keeps_files_unchanged(self):
        self.capture(self.low, 100)
        self.capture(self.high, 60000)
        before = (self.low.read_bytes(), self.high.read_bytes())
        report = calibration.summarize(self.low, self.high)
        for i, name in enumerate(('deck_a', 'deck_b', 'crossfader')):
            bounds = report['candidate_bounds'][name]
            self.assertEqual((bounds['minimum'], bounds['maximum']),
                             (103 + i * 100, 60000 + i * 100))
            self.assertEqual(bounds['low_windows'], 2)
        self.assertFalse(report['firmware_modified'])
        self.assertEqual(len(report['inputs']['low']['sha256']), 64)
        self.assertEqual(before, (self.low.read_bytes(), self.high.read_bytes()))

    def test_cli_reports_candidates_and_rejects_corrupt_input_without_json(self):
        self.capture(self.low, 100)
        self.capture(self.high, 60000)
        command = [sys.executable, str(path), '--low', str(self.low), '--high', str(self.high)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'candidate_bounds_only')
        self.high.write_text('not a capture')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('Calibration capture rejected', result.stderr)

    def test_rejects_missing_reordered_and_partial_windows(self):
        self.capture(self.low, 100)
        original = self.low.read_text()
        for bad in (original.replace('A1,', 'A3,'),
                    '\n'.join(original.splitlines()[:-2]),
                    'control,min,max,mean,span\nA0,1,2,1.5,1\n'):
            with self.subTest(capture=bad):
                self.low.write_text(bad)
                with self.assertRaises(ValueError):
                    calibration.read_capture(self.low)

    def test_rejects_bad_ranges_nonfinite_means_and_corrupt_columns(self):
        self.capture(self.low, 100)
        original = self.low.read_text()
        for bad in (original.replace('A0,100,102,101,2', row) for row in (
                'A0,-1,102,101,103', 'A0,100,65536,101,65436',
                'A0,100,102,nan,2', 'A0,100,102,103,2',
                'A0,100,102,101,3', 'A0,100,102,101',
                'A0,100,102,101,2,extra')):
            self.low.write_text(bad)
            with self.assertRaises(ValueError):
                calibration.read_capture(self.low)

    def test_rejects_overlapping_or_swapped_stops(self):
        for low, high in ((100, 101), (60000, 100)):
            self.capture(self.low, low)
            self.capture(self.high, high)
            with self.assertRaisesRegex(ValueError, 'overlap or are reversed'):
                calibration.summarize(self.low, self.high)


if __name__ == '__main__':
    unittest.main()
