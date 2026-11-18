# Contributing to Mini-MIDI

## Where changes belong

| Change | Location |
| --- | --- |
| CircuitPython application or MIDI logic | `firmware/` |
| Temporary on-board diagnostics | `tools/` |
| Desktop logic and application simulations | `tests/` |
| Setup, wiring, MIDI mappings and research | `docs/` |
| Documentation photos | `docs/images/` |
| PCB project, local footprints and design checks | `hardware/pcb/` |
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

## Automated desktop checks

[Desktop checks](.github/workflows/desktop-checks.yml) runs source compilation and the unittest suite on pull requests, pushes to `main` and manual dispatch. The matrix uses Ubuntu 24.04 and Windows Server 2025 with Python 3.12 and 3.14. It installs no Python packages; the firmware and calibration simulations use the standard library. The official checkout/setup actions are pinned to reviewed commit SHAs, with read-only repository permissions and checkout credential persistence disabled.

The default jobs do **not** install KiCad: PCB integration tests explicitly skip when `pcbnew`/`kicad-cli` are unavailable. A green desktop job is not an ERC/DRC result or hardware validation. Before modifying PCB sources, also run the [KiCad checks](hardware/pcb/README.md#recheck-after-edits) locally and report any skipped tests separately. Firmware still requires CircuitPython/KB2040 bench testing.

Workflow references reviewed 2026-11-18: [GitHub Python testing guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/python), [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) and [setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0). The matrix checks desktop Python compatibility; it does not establish CircuitPython runtime compatibility.
