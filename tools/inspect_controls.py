"""Temporary KB2040 bench program; copy to CIRCUITPY/code.py to run.

Reports raw ADC windows and active-low switch states. Does not send MIDI.
"""
import time

SAMPLES_PER_WINDOW = 100
SAMPLE_DELAY = 0.005


def read_window(pots, switches, samples=SAMPLES_PER_WINDOW, delay=SAMPLE_DELAY):
    """Return per-pot (min, max, mean) and final raw digital levels.

    The window spans samples * delay plus reading/printing overhead. It is not
    a measured sample rate, oscilloscope trace, or automatic calibration.
    """
    if samples < 1:
        raise ValueError("At least one sample is required")
    totals = [0] * len(pots)
    minima = [65535] * len(pots)
    maxima = [0] * len(pots)
    for _ in range(samples):
        for i, pot in enumerate(pots):
            value = pot.value
            totals[i] += value
            minima[i] = min(minima[i], value)
            maxima[i] = max(maxima[i], value)
        time.sleep(delay)
    stats = [(minima[i], maxima[i], totals[i] / samples) for i in range(len(pots))]
    return stats, tuple(pin.value for pin in switches)


def main():
    # Lazy imports let desktop tests exercise read_window without board modules.
    import analogio
    import board
    import digitalio

    resources = []
    try:
        pots = []
        for name in ("A0", "A1", "A2"):
            pin = analogio.AnalogIn(getattr(board, name))
            resources.append(pin)
            pots.append(pin)
        switches = []
        for name in ("D2", "D3", "D4", "D5", "D6"):
            pin = digitalio.DigitalInOut(getattr(board, name))
            resources.append(pin)
            pin.switch_to_input(pull=digitalio.Pull.UP)
            switches.append(pin)
        print("Bench mode: no MIDI. Hold pots still for each measurement window.")
        print("Pot labels: A0=deck_a, A1=deck_b, A2=crossfader; switches: 0=grounded/on.")
        while True:
            stats, levels = read_window(pots, switches)
            for name, (low, high, mean) in zip(("A0", "A1", "A2"), stats):
                print("{} min={} max={} mean={:.1f} span={}".format(
                    name, low, high, mean, high - low))
            print("Raw switch levels D2 D3 D4 D5 D6:", levels)
    finally:
        for pin in reversed(resources):
            pin.deinit()


if __name__ == "__main__":
    main()
