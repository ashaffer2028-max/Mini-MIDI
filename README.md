# Mini-MIDI

A handheld USB MIDI controller for practicing DJ mixes on the go. Built around an **Adafruit KB2040**, CircuitPython, three potentiometers and four physical switches. It sends control messages to DJ software; audio comes from the host.

![Mini-MIDI prototype](docs/images/prototype-01.jpeg)

## Start here

1. Read the [wiring and candidate parts guide](docs/HARDWARE.md).
2. Follow [installation, calibration and troubleshooting](docs/SETUP.md). Copy `firmware/code.py` and `firmware/midi_logic.py` to the **root of CIRCUITPY**.
3. Map the controls in your DJ software using the [MIDI mapping table](docs/MIDI_MAPPING.md).

The active firmware is revision 2, with independent switch debounce, per-pot calibration and USB MIDI startup diagnostics. **Physical KB2040 validation is still pending.** Shared pots send their current positions when modes change, so software parameters can jump.

## Repository layout

| Location | Contents |
| --- | --- |
| [`firmware/`](firmware/) | Current CircuitPython application and reusable MIDI logic |
| [`hardware/`](hardware/README.md) | Hardware file index and enclosure CAD export |
| [`docs/`](docs/README.md) | Setup, wiring, parts, MIDI mapping and technical resources |
| [`docs/images/`](docs/images/) | Prototype photos used in documentation |
| [`tools/`](tools/README.md) | Temporary on-board diagnostics for collecting real calibration readings |
| [`tests/`](tests/) | Desktop unit tests and simulated firmware-loop tests |
| [`archive/`](archive/README.md) | Original firmware snapshots, preserved for reference |

## Development

Run from the repository root with Python 3:

```sh
python -m unittest discover -s tests -v
python -m py_compile firmware/code.py firmware/midi_logic.py
```

Desktop tests cover logic and simulated application behavior. They do not establish CircuitPython runtime compatibility, USB enumeration, ADC noise, wiring correctness or physical latency.

See [contribution guidance](CONTRIBUTING.md) for file placement, validation and hardware evidence.
