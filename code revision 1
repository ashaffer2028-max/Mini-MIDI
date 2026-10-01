import time
import board
import analogio
import digitalio
import usb_midi
import microcontroller
import adafruit_midi
from adafruit_midi.control_change import ControlChange

# ==============================================================================
# PIN & HARDWARE CONFIGURATION
# ==============================================================================

# Potentiometers (Analog Inputs)
pot_deck_a = analogio.AnalogIn(board.A0)       # Pot 1: Left Deck
pot_deck_b = analogio.AnalogIn(board.A1)       # Pot 2: Right Deck
pot_crossfader = analogio.AnalogIn(board.A2)   # Pot 3: Rotary Crossfader

# Switch 1: SPST (D2) -> Global Filter / Hold 3s for Hardware Reboot
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
JITTER_THRESHOLD = 2    # Ignore ADC jitter <= 2 MIDI steps
EMA_ALPHA = 0.12        # High smoothing factor for stable values
RESET_HOLD_TIME = 3.0   # Hold D2 switch ON for 3s to reboot board

# Raw ADC Calibration Boundaries (Guarantees full 0-127 reach)
ADC_MIN = 800
ADC_MAX = 64700

# State Buffers
ema_vals = {"deck_a": None, "deck_b": None, "crossfader": None}
last_sent_vals = {"deck_a": -1, "deck_b": -1, "crossfader": -1}
last_cc = {"deck_a": -1, "deck_b": -1}

# Pre-read startup state to eliminate phantom MIDI on plugin
last_extra_state = not spst_extra.value
switch_on_time = None

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

    # 3. Scaled Mapping with Clamping to guarantee 0 and 127 endpoints
    clamped_raw = max(ADC_MIN, min(ADC_MAX, ema_vals[key]))
    midi_val = int(((clamped_raw - ADC_MIN) * 127) / (ADC_MAX - ADC_MIN))
    
    return max(0, min(127, midi_val))

def should_send_midi(new_val, last_sent):
    """Validates whether new values cross deadband threshold or physical bounds."""
    if last_sent == -1:
        return True
    if abs(new_val - last_sent) >= JITTER_THRESHOLD:
        return True
    if (new_val == 0 or new_val == 127) and new_val != last_sent:
        return True
    return False

# ==============================================================================
# MAIN LOOP
# ==============================================================================

while True:
    now = time.monotonic()

    # 1. READ SWITCH STATES & HANDLE HARDWARE RESET
    is_d5_on = not spst_d5.value           # Split Mode (Left Vol / Right Filter)
    is_filter_mode = not spst_filter.value # Global Filter Mode

    # Hardware Reboot Logic (Hold D2 switch for 3 seconds)
    if is_filter_mode:
        if switch_on_time is None:
            switch_on_time = now
        elif now - switch_on_time >= RESET_HOLD_TIME:
            print("Rebooting KB2040...")
            time.sleep(0.05)
            microcontroller.reset()
    else:
        switch_on_time = None

    # Read DPDT Switch (HIGH / MID / LOW)
    if not dpdt_pin1.value and dpdt_pin6.value:
        eq_state = "HIGH"
    elif dpdt_pin1.value and not dpdt_pin6.value:
        eq_state = "LOW"
    else:
        eq_state = "MID"

    # Read Assignable Switch (D6 -> CC 13)
    extra_active = not spst_extra.value
    if extra_active != last_extra_state:
        midi.send(ControlChange(13, 127 if extra_active else 0))
        last_extra_state = extra_active

    # 2. READ & SMOOTH POTENTIOMETERS
    val_a = get_smoothed_adc(pot_deck_a, "deck_a")
    val_b = get_smoothed_adc(pot_deck_b, "deck_b")
    val_xfader = get_smoothed_adc(pot_crossfader, "crossfader")

    # 3. ROUTE CC NUMBERS ACCORDING TO SWITCH PRIORITIES
    if is_d5_on:
        cc_deck_a = 14  # Left Pot -> Deck A Volume
        cc_deck_b = 11  # Right Pot -> Deck B Filter
    elif is_filter_mode:
        cc_deck_a = 10  # Left Pot -> Deck A Filter
        cc_deck_b = 11  # Right Pot -> Deck B Filter
    else:
        if eq_state == "HIGH":
            cc_deck_a, cc_deck_b = 1, 2
        elif eq_state == "MID":
            cc_deck_a, cc_deck_b = 3, 4
        elif eq_state == "LOW":
            cc_deck_a, cc_deck_b = 5, 6

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

    time.sleep(0.002)  # Ultra-fast 2ms loop execution (~500 Hz sample rate)
