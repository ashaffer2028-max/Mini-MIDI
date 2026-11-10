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

Switch states are accepted after the whole input tuple remains unchanged for 20ms. This suppresses short contact bounces while preserving the previous priority and CC assignments. Actual acceptance time includes loop overhead. A selector intermediate state lasting longer than the debounce interval can still be accepted.

ADC oversampling, EMA smoothing and calibration defaults are inherited from revision 1. `ADC_MIN=800` and `ADC_MAX=64700` are starting values, not measured guarantees for every build. Measure each pot at both stops, check stability, then adjust bounds if needed. Smaller EMA alpha means more smoothing and more response delay. The 2ms sleep does not establish a measured 500Hz loop rate.

D6 intentionally sends no startup CC; toggle it after connecting if the software's initial state differs. All pots send an initial value, and mode changes resend their physical positions.

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
