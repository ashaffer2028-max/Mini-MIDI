# Contributing to Mini-MIDI

## Where changes belong

| Change | Location |
| --- | --- |
| CircuitPython application or MIDI logic | `firmware/` |
| Temporary on-board diagnostics | `tools/` |
| Desktop logic and application simulations | `tests/` |
| Setup, wiring, MIDI mappings and research | `docs/` |
| Documentation photos | `docs/images/` |
| Editable enclosure models and CAD exports | `hardware/cad/` |
| Preserved old implementation snapshots | `archive/firmware/` |

Use descriptive filenames without spaces. Update relative links when moving files. Keep supplier URLs, exact candidate part numbers and source review dates with the relevant hardware notes.

## Validate a change

Run from the repository root:

```sh
python -m unittest discover -s tests -v
python -m py_compile firmware/code.py firmware/midi_logic.py
```

Tests run on desktop Python. Simulated pin and USB objects do not validate electrical behavior or CircuitPython hardware compatibility. Record physical results separately using the [bench checklist](docs/SETUP.md#bench-checklist--pending-physical-execution), including board/library versions, measured calibration values and host software.

For firmware deployment, copy only `firmware/code.py` and `firmware/midi_logic.py` to the root of `CIRCUITPY`, plus the required library described in [setup](docs/SETUP.md). Keep development tests and historical snapshots on the computer.

## Review

Use focused commits and a pull request. Explain the changed behavior and the checks performed. Preserve existing MIDI assignments unless a change is intentional and documented in the [mapping guide](docs/MIDI_MAPPING.md).

Keep generated Python caches and virtual environments out of commits. Treat candidate parts, supplier availability, physical measurements and completed tests as separate facts; record only evidence actually obtained.
