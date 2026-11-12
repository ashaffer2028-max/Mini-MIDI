# Setup and validation

## Install

1. Back up the current contents of `CIRCUITPY`.
2. Install the stable CircuitPython build **for Adafruit KB2040** from the [board download page](https://circuitpython.org/board/adafruit_kb2040/), following the [official installation guide](https://learn.adafruit.com/adafruit-kb2040/circuitpython).
3. From the [CircuitPython library bundle](https://circuitpython.org/libraries), choose the bundle matching the installed CircuitPython major version. Copy its `adafruit_midi` directory into `CIRCUITPY/lib/`.
4. Copy `firmware/code.py` and `firmware/midi_logic.py` to the root of `CIRCUITPY`. Both files are required. `board`, `analogio`, `digitalio` and `usb_midi` are provided by the firmware.
5. Reconnect with a USB data cable. Check the serial console for import errors, then select the device in your host's MIDI settings.
6. Use the README mapping table to MIDI-learn each control. Enable software pickup/soft takeover if supported.

## Revision 2 behavior

The original D2 filter switch also triggered a reboot after three seconds. A maintained switch could therefore reset the board repeatedly during ordinary filter use. Revision 2 removes that timer; use the board's physical reset facility when needed.

Each physical switch is accepted after its input remains unchanged for 20ms. D2, D5 and D6 have independent timers, so chatter on one cannot postpone another control. The two EQ contacts share one timer to keep their transition together. This suppresses short contact bounces while preserving the previous priority and CC assignments. Actual acceptance time includes loop overhead. A selector intermediate state lasting longer than the debounce interval can still be accepted.

ADC oversampling, EMA smoothing and calibration defaults are inherited from revision 1. Each entry in `pot_ranges` starts at `PotRange(800, 64700)`, not a measured guarantee for every build. The three pots can now be calibrated independently. Smaller EMA alpha means more smoothing and more response delay. The 2ms sleep does not establish a measured 500Hz loop rate.

## Measure and enter per-pot bounds

1. Start revision 2 normally, then interrupt it with Ctrl-C in the CircuitPython serial console. MIDI transmission stops while measuring; the initialized `pot_deck_a`, `pot_deck_b` and `pot_crossfader` objects remain available in that session.
2. With all pots at their low-output stops, run `print(pot_deck_a.value, pot_deck_b.value, pot_crossfader.value)` repeatedly. Record a range of settled readings for each pot, not one outlier. Repeat at the high-output stops. Raw values increasing in the wrong physical direction indicate reversed outer terminals; calibration does not reverse polarity.
3. Edit only that pot's `PotRange(minimum, maximum)` pair in `firmware/code.py`. Choose the lower bound near the upper edge of the settled low-stop readings and the upper bound near the lower edge of high-stop readings, so small endpoint noise stays clamped. Avoid wide margins that discard useful travel. If the two stop ranges overlap or the measured span is unexpectedly narrow, check wiring before calibrating around it.
4. Bounds must satisfy `0 <= minimum < maximum <= 65535`; invalid bounds raise `ValueError` at startup instead of dividing by zero or reversing the scale. This check does not prove that a physical range is healthy.
5. Save both firmware files to `CIRCUITPY` and press Ctrl-D to restart if the console remains stopped. After the EMA settles, verify 0 and 127 at the stops and a smooth sweep in a MIDI monitor. Record the settings and any idle jitter. The middle position still uses a linear mapping, not center-detent calibration.

CircuitPython exposes `AnalogIn.value` on a 0–65535 scale even with a lower-resolution ADC; this is not a claim of 16-bit physical accuracy. Source reviewed 2026-11-11: [official analogio API](https://docs.circuitpython.org/en/stable/shared-bindings/analogio/index.html#analogio.AnalogIn.value). No endpoint measurements have been taken for this repository.

D6 intentionally sends no startup CC; toggle it after connecting if the software's initial state differs. All pots send an initial value, and mode changes resend their physical positions.

## USB MIDI troubleshooting

If startup reports **USB MIDI output unavailable**, the program found fewer than two USB MIDI ports. It stops before initializing control pins, instead of failing later with an index error. This check does not prove the host can see or use the device.

1. Inspect an existing `boot.py` for `usb_midi.disable()`. USB MIDI is normally enabled by default. Back up the file before editing; preserve other custom setup.
2. If MIDI was deliberately disabled, remove that call or replace it with `usb_midi.enable()` in `boot.py`. Do not put USB enable/disable calls in `code.py`: the USB device setup has already happened by then. No `boot.py` is required for the ordinary default configuration.
3. Perform a hard reset with the board reset button or unplug/replug USB. Saving a file or Ctrl-D alone does not rerun `boot.py`. Check `boot_out.txt` and the serial console for boot errors or safe-mode messages.
4. If ports exist but the host shows no MIDI device, check the data cable, host MIDI settings and USB connection. Do not erase firmware or disable other interfaces without evidence of the cause. A USB endpoint-allocation error is a separate boot issue; follow the official guide before changing interfaces.

Sources reviewed 2026-11-12: [CircuitPython usb_midi API](https://docs.circuitpython.org/en/stable/shared-bindings/usb_midi/) and [Adafruit USB setup/reset guidance](https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/circuitpy-midi-serial). Missing-port behavior is covered by simulated startup tests; enumeration and recovery still need a real KB2040.

## Bench checklist — pending physical execution

- [ ] Check wiring against the electrical table, especially selector contacts and 3.3V pot supply.
- [ ] Confirm USB MIDI enumeration and MIDI channel 1 output.
- [ ] Sweep each pot to both stops; verify 0/127 and inspect idle jitter.
- [ ] Check all EQ positions and the D5-over-D2 priority.
- [ ] Leave D2 on for at least 30 seconds: filter control must keep working without USB disconnects.
- [ ] Toggle D6 repeatedly: one CC 13 transition per settled switch change, with no short bounce bursts.
- [ ] Change mode without moving pots: new CC gets the current physical position. Assess parameter jumps before live use.
- [ ] Check reconnect behavior and D6 host synchronization.
- [ ] Record CircuitPython/library versions, actual component models, calibration measurements and host application.

Desktop checks: `python -m unittest discover -s tests -v` and `python -m py_compile firmware/code.py firmware/midi_logic.py`. Hardware testing remains necessary even when these pass.

Debounce design reference reviewed 2026-11-12: [Adafruit Debouncer API](https://docs.circuitpython.org/projects/debouncer/en/latest/api.html). Mini-MIDI retains its own small polling helper and adds no library dependency. Independent timers are a project design choice; the firmware-loop regression tests reproduce unrelated-switch chatter using simulated inputs, not physical contacts.
