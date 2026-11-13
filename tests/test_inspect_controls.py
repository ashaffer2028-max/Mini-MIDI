import contextlib
import importlib.util
import io
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

path = pathlib.Path(__file__).resolve().parents[1] / 'tools/inspect_controls.py'
spec = importlib.util.spec_from_file_location('inspect_controls', path)
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


class SequencePin:
    def __init__(self, values):
        self.values = iter(values)

    @property
    def value(self):
        return next(self.values)


class DiagnosticTests(unittest.TestCase):
    def test_window_stats_are_independent_and_reset_each_time(self):
        pots = [SequencePin([100, 300, 200, 900]), SequencePin([0, 65535, 0, 800])]
        switches = [SequencePin([True, False]), SequencePin([False, True])]
        with patch.object(diagnostic.time, 'sleep'):
            stats, levels = diagnostic.read_window(pots, switches, samples=3)
            self.assertEqual(stats, [(100, 300, 200), (0, 65535, 21845)])
            self.assertEqual(levels, (True, False))
            stats, levels = diagnostic.read_window(pots, switches, samples=1)
            self.assertEqual(stats, [(900, 900, 900), (800, 800, 800)])
            self.assertEqual(levels, (False, True))

    def test_empty_window_is_rejected(self):
        with self.assertRaises(ValueError):
            diagnostic.read_window([], [], samples=0)

    def test_main_configures_inputs_and_releases_all_pins_when_interrupted(self):
        allocated = []

        class Pin:
            value = 123
            def __init__(self, name):
                self.name = name
                self.released = False
                self.pull = None
                allocated.append(self)
            def switch_to_input(self, pull):
                self.pull = pull
            def deinit(self):
                self.released = True

        names = ('A0', 'A1', 'A2', 'D2', 'D3', 'D4', 'D5', 'D6')
        board = types.SimpleNamespace(**dict(zip(names, names)))
        digital = types.SimpleNamespace(DigitalInOut=Pin, Pull=types.SimpleNamespace(UP='up'))
        analog = types.SimpleNamespace(AnalogIn=Pin)
        with patch.dict(sys.modules, board=board, digitalio=digital, analogio=analog):
            with patch.object(diagnostic, 'read_window', side_effect=KeyboardInterrupt):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(KeyboardInterrupt):
                        diagnostic.main()
        self.assertEqual([p.name for p in allocated], list(names))
        self.assertTrue(all(p.released for p in allocated))
        self.assertTrue(all(p.pull == 'up' for p in allocated[3:]))


if __name__ == '__main__':
    unittest.main()
