# Revision 2: based on code revision 1; bench validation pending.
import time
import board
import analogio
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from midi_logic import PotRange, StableSwitches, select_cc, should_send_midi

# USB devices are configured in boot.py, before this application starts.
# Explain a disabled/missing MIDI interface before allocating control pins.
if len(usb_midi.ports) < 2:
    raise RuntimeError(
        "USB MIDI output unavailable. Check boot.py for usb_midi.disable(); "
        "enable MIDI there and hard-reset the board. See docs/SETUP.md."
    )

# ==============================================================================
# PIN & HARDWARE CONFIGURATION
# ==============================================================================

# Potentiometers (Analog Inputs)
pot_deck_a = analogio.AnalogIn(board.A0)       # Pot 1: Left Deck
pot_deck_b = analogio.AnalogIn(board.A1)       # Pot 2: Right Deck
pot_crossfader = analogio.AnalogIn(board.A2)   # Pot 3: Rotary Crossfader

# Switch 1: SPST (D2) -> Global Filter (no timed reboot)
spst_filter = digitalio.DigitalInOut(board.D2)
spst_filter.direction = digitalio.Direction.INPUT
spst_filter.pull = digitalio.Pull.UP            

# Switch 2: DPDT 3-Way (D3 & D4) -> EQ Band Selection (HIGH / MID / LOW)
dpdt_pin1 = digitalio.DigitalInOut(board.D3)
dpdt_pin1.direction = digitalio.Direction.INPUT
dpdt_pin1.pull = digitalio.Pull.UP

dpdt_pin6 = digitalio.DigitalInOut(board.D4)
dpdt_pin6.direction = digitalio.Direction.INPUT
dpdt_pin6.pull = digitalio.Pull.UP

# Switch 3: SPST (D5) -> Split Mode (Left = Vol CC 14, Right = Filter CC 11)
spst_d5 = digitalio.DigitalInOut(board.D5)
spst_d5.direction = digitalio.Direction.INPUT
spst_d5.pull = digitalio.Pull.UP

# Switch 4: SPST (D6) -> Assignable Toggle (CC 13)
spst_extra = digitalio.DigitalInOut(board.D6)
spst_extra.direction = digitalio.Direction.INPUT
spst_extra.pull = digitalio.Pull.UP

# ==============================================================================
# MIDI & SIGNAL PROCESSING CONFIGURATION
# ==============================================================================

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# Performance & Anti-Jitter Tuning
OVERSAMPLE_COUNT = 6    # Reduced sample overhead for fast loop execution
EMA_ALPHA = 0.12        # High smoothing factor for stable values
DEBOUNCE_SECONDS = 0.020  # Each physical control settles independently

# Per-pot raw ADC bounds; inherited defaults, not measured calibration.
# Edit each pair independently after measuring that pot at both stops.
pot_ranges = {
    "deck_a": PotRange(800, 64700),
    "deck_b": PotRange(800, 64700),
    "crossfader": PotRange(800, 64700),
}

# State Buffers
ema_vals = {"deck_a": None, "deck_b": None, "crossfader": None}
last_sent_vals = {"deck_a": -1, "deck_b": -1, "crossfader": -1}
last_cc = {"deck_a": -1, "deck_b": -1}

# Pre-read startup state to eliminate phantom MIDI on plugin
last_extra_state = not spst_extra.value
startup_time = time.monotonic()
switches = {
    "filter": StableSwitches((spst_filter.value,), startup_time, DEBOUNCE_SECONDS),
    "eq": StableSwitches((dpdt_pin1.value, dpdt_pin6.value), startup_time, DEBOUNCE_SECONDS),
    "split": StableSwitches((spst_d5.value,), startup_time, DEBOUNCE_SECONDS),
    "extra": StableSwitches((spst_extra.value,), startup_time, DEBOUNCE_SECONDS),
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_smoothed_adc(pin, key):
    """Fast oversampling + EMA filter with endpoint range clamping."""
    # 1. Optimized Oversampling
    raw_sum = sum(pin.value for _ in range(OVERSAMPLE_COUNT))
    raw_avg = raw_sum / OVERSAMPLE_COUNT

    # 2. Exponential Moving Average
    if ema_vals[key] is None:
        ema_vals[key] = raw_avg
    else:
        ema_vals[key] = (EMA_ALPHA * raw_avg) + ((1.0 - EMA_ALPHA) * ema_vals[key])

    # 3. Clamp and scale using this pot's calibrated range.
    return pot_ranges[key].to_midi(ema_vals[key])

# ==============================================================================
# MAIN LOOP
# ==============================================================================

while True:
    now = time.monotonic()

    # Separate physical controls cannot restart each other's debounce timer.
    # Keep the two EQ contacts together to avoid accepting a mixed transition.
    filter_high, = switches["filter"].update((spst_filter.value,), now)
    eq_high, eq_low = switches["eq"].update((dpdt_pin1.value, dpdt_pin6.value), now)
    split_high, = switches["split"].update((spst_d5.value,), now)
    extra_high, = switches["extra"].update((spst_extra.value,), now)
    is_d5_on = not split_high
    is_filter_mode = not filter_high

    # Read Assignable Switch (D6 -> CC 13)
    extra_active = not extra_high
    if extra_active != last_extra_state:
        midi.send(ControlChange(13, 127 if extra_active else 0))
        last_extra_state = extra_active

    # 2. READ & SMOOTH POTENTIOMETERS
    val_a = get_smoothed_adc(pot_deck_a, "deck_a")
    val_b = get_smoothed_adc(pot_deck_b, "deck_b")
    val_xfader = get_smoothed_adc(pot_crossfader, "crossfader")

    # 3. ROUTE CC NUMBERS ACCORDING TO SWITCH PRIORITIES
    cc_deck_a, cc_deck_b = select_cc(
        is_d5_on, is_filter_mode, eq_high, eq_low
    )

    # 4. TRANSMIT MIDI DATA
    # Transmits on value movement OR instantly when mode switch occurs
    if should_send_midi(val_a, last_sent_vals["deck_a"]) or cc_deck_a != last_cc["deck_a"]:
        midi.send(ControlChange(cc_deck_a, val_a))
        last_sent_vals["deck_a"] = val_a
        last_cc["deck_a"] = cc_deck_a

    if should_send_midi(val_b, last_sent_vals["deck_b"]) or cc_deck_b != last_cc["deck_b"]:
        midi.send(ControlChange(cc_deck_b, val_b))
        last_sent_vals["deck_b"] = val_b
        last_cc["deck_b"] = cc_deck_b

    if should_send_midi(val_xfader, last_sent_vals["crossfader"]):
        midi.send(ControlChange(9, val_xfader))
        last_sent_vals["crossfader"] = val_xfader

    time.sleep(0.002)  # Minimum sleep only; ADC, filtering and USB add overhead
