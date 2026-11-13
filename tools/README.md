# KB2040 bench tools

[`inspect_controls.py`](inspect_controls.py) reports raw pot minimum, maximum, mean and span for each measurement window, followed by the final raw levels of D2–D6. It sends no MIDI and writes no calibration values. It uses only CircuitPython built-in modules.

## Run on the board

1. Back up the current `CIRCUITPY/code.py` to your computer, including any custom calibration. Close the DJ application while measuring.
2. Temporarily copy `tools/inspect_controls.py` onto the board **as `code.py`**, replacing the backed-up application. Hard-reset the board to release the previous program's pin allocations. Do not run this alongside the controller firmware or import it into an interrupted controller session that still owns the pins.
3. Open the serial console. Hold each pot still at its low-output stop for several windows, then repeat at its high-output stop and center. Copy the actual results and identify each position. Do not use the min/max from a moving sweep as the idle noise measurement.
4. Toggle each switch. `False`/0 means grounded; `True`/1 means open. Check D3/D4 together against the [EQ selector table](../docs/HARDWARE.md#eq-selector-electrical-contract). Only the final switch levels of each window are reported; this is not a bounce trace.
5. Stop with Ctrl-C. The program releases its pins in `finally`. Restore the saved controller `code.py` and ensure `midi_logic.py` and `lib/adafruit_midi/` are still present, then hard-reset and check MIDI output.

The default window takes 100 samples, sleeping 5ms after each set of pot reads. Reading and printing add overhead; there is no measured sampling-rate guarantee. Statistics reset every window. The span is raw max minus min, not voltage, ADC accuracy, or a MIDI jitter score. Inspect several stationary windows before selecting independent [pot calibration bounds](../docs/SETUP.md#measure-and-enter-per-pot-bounds).

This tool has desktop tests with simulated inputs. **It has not been run on the physical prototype.** No measurements are supplied as if they came from your board.

API references reviewed 2026-11-13: [analogio](https://docs.circuitpython.org/en/stable/shared-bindings/analogio/) and [digitalio](https://docs.circuitpython.org/en/stable/shared-bindings/digitalio/). The tool uses `AnalogIn.value`, input pull-ups, and `deinit()` to release resources. USB MIDI may remain enumerated by CircuitPython, but this program sends no MIDI messages.
