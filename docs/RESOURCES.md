# Technical resources

Reviewed 2026-11-10. Prefer these primary sources when changing the build.

| Resource | Use in Mini-MIDI |
| --- | --- |
| [KB2040 pinouts](https://learn.adafruit.com/adafruit-kb2040/pinouts) | Verify board power rails and GPIO labels before wiring |
| [KB2040 CircuitPython installation](https://learn.adafruit.com/adafruit-kb2040/circuitpython) | Install/recover the board firmware |
| [KB2040 firmware download](https://circuitpython.org/board/adafruit_kb2040/) | Select the correct board build |
| [CircuitPython libraries](https://circuitpython.org/libraries) | Obtain a matching library bundle |
| [Adafruit MIDI API](https://docs.circuitpython.org/projects/midi/en/latest/api.html) | `ControlChange` and zero-based output channel configuration |
| [Adafruit MIDI examples](https://docs.circuitpython.org/projects/midi/en/stable/examples.html) | Compare USB MIDI initialization with maintained examples |
| [Adafruit MIDI source](https://github.com/adafruit/Adafruit_CircuitPython_MIDI) | Investigate library behavior and compatibility |

The hardware page separates identified product candidates from general supplier links. Before selecting a new SKU, add its manufacturer datasheet, exact part number, dimensions and electrical compatibility. Never treat a supplier homepage as evidence that a specific part fits.

## Useful next revisions

- Measure per-pot ADC endpoints and latency on the physical controller.
- Evaluate pickup/soft takeover for shared EQ/filter pots; bidirectional host feedback would need a defined protocol and software mapping.
- Record the actual selector's continuity table and component dimensions before enclosure refinement.
