import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'firmware'))
from midi_logic import PotRange, StableSwitches, select_cc, should_send_midi


class CalibrationTests(unittest.TestCase):
    def test_defaults_preserve_previous_mapping_for_full_adc_domain(self):
        scale = PotRange(800, 64700)
        for raw in range(65536):
            clamped = max(800, min(64700, raw))
            expected = int((clamped - 800) * 127 / (64700 - 800))
            self.assertEqual(scale.to_midi(raw), expected)

    def test_fractional_ema_input(self):
        scale = PotRange(1000, 64000)
        self.assertEqual(scale.to_midi(32500.5), 63)

    def test_endpoints_clamp_outside_calibration(self):
        scale = PotRange(1000, 64000)
        for raw in (0, 999, 1000):
            self.assertEqual(scale.to_midi(raw), 0)
        for raw in (64000, 64001, 65535):
            self.assertEqual(scale.to_midi(raw), 127)

    def test_independent_pot_ranges(self):
        deck_a = PotRange(1000, 64000)
        deck_b = PotRange(2000, 62000)
        self.assertEqual(deck_a.to_midi(62000), 122)
        self.assertEqual(deck_b.to_midi(62000), 127)

    def test_invalid_ranges_fail_at_construction(self):
        for low, high in ((800, 800), (64700, 800), (-1, 64000), (0, 65536)):
            with self.subTest(low=low, high=high):
                with self.assertRaises(ValueError):
                    PotRange(low, high)

    def test_custom_range_is_monotonic_and_bounded(self):
        scale = PotRange(1200, 63000)
        values = [scale.to_midi(raw) for raw in range(65536)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(set(values), set(range(128)))


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
