"""Run real code.py with scripted pins, a fake clock and captured MIDI output.

These tests exercise application wiring and behavior, not CircuitPython/USB hardware.
"""
import pathlib
import runpy
import sys
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'firmware'))


class EndFrames(Exception):
    pass


def run_firmware(frames, ports=(object(), object())):
    """Each frame is (monotonic time, pin overrides); unspecified pins default high."""
    index = 0
    sent = []

    class Pin:
        def __init__(self, name):
            self.name = name

        @property
        def value(self):
            default = 32768 if self.name.startswith('A') else True
            return frames[index][1].get(self.name, default)

    def sleep(_):
        nonlocal index
        index += 1
        if index >= len(frames):
            raise EndFrames()

    class Midi:
        def __init__(self, midi_out, out_channel):
            self.channel = out_channel
            assert midi_out is ports[1]

        def send(self, message):
            sent.append((frames[index][0], self.channel, message.control, message.value))

    class ControlChange:
        def __init__(self, control, value):
            self.control = control
            self.value = value

    board = types.ModuleType('board')
    for name in ('A0', 'A1', 'A2', 'D2', 'D3', 'D4', 'D5', 'D6'):
        setattr(board, name, name)
    digital = types.ModuleType('digitalio')
    digital.DigitalInOut = Pin
    digital.Direction = types.SimpleNamespace(INPUT=1)
    digital.Pull = types.SimpleNamespace(UP=1)
    analog = types.ModuleType('analogio')
    analog.AnalogIn = Pin
    clock = types.ModuleType('time')
    clock.monotonic = lambda: frames[index][0]
    clock.sleep = sleep
    usb = types.ModuleType('usb_midi')
    usb.ports = ports
    midi = types.ModuleType('adafruit_midi')
    midi.MIDI = Midi
    cc = types.ModuleType('adafruit_midi.control_change')
    cc.ControlChange = ControlChange
    modules = dict(board=board, digitalio=digital, analogio=analog, time=clock,
                   usb_midi=usb, adafruit_midi=midi)
    modules['adafruit_midi.control_change'] = cc
    with patch.dict(sys.modules, modules):
        try:
            runpy.run_path(str(ROOT / 'firmware/code.py'))
        except EndFrames:
            pass
    return sent


class FirmwareTests(unittest.TestCase):
    def test_missing_usb_output_has_actionable_startup_error(self):
        for ports in ((), (object(),)):
            with self.subTest(port_count=len(ports)):
                with self.assertRaisesRegex(RuntimeError, 'USB MIDI output unavailable.*boot.py'):
                    run_firmware([(0, {})], ports=ports)

    def test_settled_d6_sends_one_on_and_one_off(self):
        sent = run_firmware([(0, {}), (.001, {'D6': False}),
                             (.025, {'D6': False}), (.05, {'D6': False}),
                             (.06, {}), (.085, {}), (.1, {})])
        self.assertEqual([m for m in sent if m[2] == 13],
                         [(.025, 0, 13, 127), (.085, 0, 13, 0)])

    def test_d6_chatter_cannot_starve_filter_mode(self):
        frames = [(0, {})]
        frames += [(i / 1000, {'D2': False, 'D6': bool(i % 2)})
                   for i in range(1, 41)]
        sent = run_firmware(frames)
        filters = [m for m in sent if m[2] in (10, 11)]
        self.assertEqual([m[2] for m in filters], [10, 11])
        self.assertTrue(all(.020 <= m[0] <= .023 for m in filters))
        self.assertFalse(any(m[2] == 13 for m in sent))

    def test_eq_chatter_cannot_starve_split_mode(self):
        frames = [(0, {})]
        frames += [(i / 1000, {'D5': False, 'D3': bool(i % 2)})
                   for i in range(1, 41)]
        sent = run_firmware(frames)
        self.assertEqual([m[2] for m in sent if m[0] > 0], [14, 11])

    def test_initial_ccs_and_still_pots_do_not_repeat(self):
        sent = run_firmware([(0, {}), (.01, {}), (.1, {}), (30, {})])
        self.assertEqual(sent, [(0, 0, 3, 63), (0, 0, 4, 63), (0, 0, 9, 63)])

    def test_filter_hold_does_not_reboot(self):
        sent = run_firmware([(0, {'D2': False}), (3.1, {'D2': False}),
                             (30, {'D2': False})])
        self.assertEqual([m[2] for m in sent], [10, 11, 9])


if __name__ == '__main__':
    unittest.main()
