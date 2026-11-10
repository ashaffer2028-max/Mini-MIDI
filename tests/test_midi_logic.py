import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'firmware'))
from midi_logic import StableSwitches, select_cc, should_send_midi


class RoutingTests(unittest.TestCase):
    def test_all_switch_combinations(self):
        for split, filt, high, low in itertools.product((False, True), repeat=4):
            with self.subTest(split=split, filt=filt, high=high, low=low):
                expected = ((14, 11) if split else (10, 11) if filt else
                            (1, 2) if not high and low else
                            (5, 6) if high and not low else (3, 4))
                self.assertEqual(select_cc(split, filt, high, low), expected)

    def test_filter_remains_selected_after_long_hold(self):
        switches = StableSwitches((False, True, True, True, True), 0)
        for now in (0, 1, 3, 4, 30):
            filt, high, low, split, _ = switches.update(switches.value, now)
            self.assertEqual(select_cc(not split, not filt, high, low), (10, 11))


class DebounceTests(unittest.TestCase):
    def test_startup_state(self):
        switch = StableSwitches((True, False), 0)
        self.assertEqual(switch.update((True, False), 0), (True, False))

    def test_bounce_does_not_change_output(self):
        switch = StableSwitches((True,), 0)
        for raw, now in [((False,), .001), ((True,), .010), ((False,), .015)]:
            self.assertEqual(switch.update(raw, now), (True,))
        self.assertEqual(switch.update((False,), .034), (True,))
        self.assertEqual(switch.update((False,), .036), (False,))

    def test_whole_selector_tuple_is_stable(self):
        switch = StableSwitches((False, True), 0)
        switch.update((True, True), .001)
        switch.update((True, False), .010)
        self.assertEqual(switch.update((True, False), .029), (False, True))
        self.assertEqual(switch.update((True, False), .031), (True, False))


class SendTests(unittest.TestCase):
    def test_initial_value(self):
        self.assertTrue(should_send_midi(64, -1))

    def test_deadband(self):
        self.assertFalse(should_send_midi(65, 64))
        self.assertTrue(should_send_midi(66, 64))
        self.assertTrue(should_send_midi(62, 64))

    def test_endpoints_and_no_repeats(self):
        for value, previous in [(0, 1), (127, 126)]:
            self.assertTrue(should_send_midi(value, previous))
            self.assertFalse(should_send_midi(value, value))


if __name__ == '__main__':
    unittest.main()
