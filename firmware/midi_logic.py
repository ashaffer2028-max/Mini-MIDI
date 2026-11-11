"""Hardware-independent routing and switch filtering for Mini-MIDI."""


class PotRange:
    """Map one calibrated CircuitPython ADC range to 7-bit MIDI values."""

    def __init__(self, minimum, maximum):
        if not 0 <= minimum < maximum <= 65535:
            raise ValueError("Pot range must satisfy 0 <= min < max <= 65535")
        self.minimum = minimum
        self.maximum = maximum

    def to_midi(self, raw):
        clamped = max(self.minimum, min(self.maximum, raw))
        return int((clamped - self.minimum) * 127 / (self.maximum - self.minimum))


class StableSwitches:
    """Accept a new tuple only after it stays unchanged for interval seconds."""

    def __init__(self, initial, now, interval=0.020):
        self.value = initial
        self.candidate = initial
        self.changed_at = now
        self.interval = interval

    def update(self, raw, now):
        if raw != self.candidate:
            self.candidate = raw
            self.changed_at = now
        elif now - self.changed_at >= self.interval:
            self.value = self.candidate
        return self.value


def select_cc(split_active, filter_active, eq_high, eq_low):
    """Preserve revision 1 priority and active-low selector truth table."""
    if split_active:
        return 14, 11
    if filter_active:
        return 10, 11
    if not eq_high and eq_low:
        return 1, 2
    if eq_high and not eq_low:
        return 5, 6
    return 3, 4


def should_send_midi(new_val, last_sent, threshold=2):
    """Send initial values, changes >= threshold, and changed endpoints."""
    return (last_sent == -1 or abs(new_val - last_sent) >= threshold
            or (new_val in (0, 127) and new_val != last_sent))
