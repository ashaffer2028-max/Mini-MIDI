# Initial PCB model — revision A

**Schematic and component placement draft. UNROUTED. Not for fabrication.**

This first model keeps the KB2040 module and puts three analog-control connectors plus four switch connectors on a provisional 90 × 60mm two-layer carrier. It preserves the active firmware and MIDI mappings. Read the [architecture, pin contract, sources and assumptions](DESIGN_NOTES.md) before editing or connecting hardware.

![PCB component placement, top view](rev-a/previews/board-top.svg)

The preview shows component pads, placement and 18 pin-function silkscreen labels, not finished copper routing. Open the PCB in KiCad to see the unrouted connections.

## Open and edit

Open [mini-midi-carrier.kicad_pro](rev-a/mini-midi-carrier.kicad_pro) in **KiCad 9**. The project includes:

- [Native schematic](rev-a/mini-midi-carrier.kicad_sch) and [schematic preview](rev-a/previews/mini-midi-carrier.svg).
- [Native PCB](rev-a/mini-midi-carrier.kicad_pcb), local symbols and a socketed-module footprint with project-local library tables.
- [Auditable module pad map](rev-a/module-pin-map.json), original/source header IDs and coordinates.
- [Connectivity checker](rev-a/check_connectivity.py) and [recorded check reports](rev-a/checks/).

The module symbol abstracts the purchased board as passive connection pins. ERC does not analyze the module's internal regulator, USB circuit or RP2040. Carrier pad numbering is defined in the design notes and is not a physical KB2040 silkscreen numbering scheme.

## Checks recorded on 2026-11-15

| Check | Result | What it establishes |
| --- | --- | --- |
| Schematic ERC, KiCad 9.0.2 | 0 violations | Connected labels, no-connect flags and library references pass this model's rules |
| PCB DRC | 0 geometry violations; **20 unconnected items** | Placement is free of reported geometry violations; routing is incomplete |
| Schematic/PCB parity | 0 issues | Symbol references, footprints and pad nets correspond |
| Independent connectivity audit | Pass | All 26 module pad centers, 8 firmware assignments and 24 net membership sets match |
| Physical test / enclosure fit | Not performed | No fabrication or fit readiness claim |

Do not interpret the geometry result as a completed DRC pass: the 20 unrouted connections remain blockers. No Gerbers or drill package has been released.

## Recheck after edits

From the repository root:

```sh
kicad-cli sch erc --format json --units mm -o hardware/pcb/rev-a/checks/erc.json hardware/pcb/rev-a/mini-midi-carrier.kicad_sch
kicad-cli pcb drc --schematic-parity --format json --units mm -o hardware/pcb/rev-a/checks/drc.json hardware/pcb/rev-a/mini-midi-carrier.kicad_pcb
python3 hardware/pcb/rev-a/check_connectivity.py
```

Use the Python interpreter supplied with KiCad or one with `pcbnew` installed (the recorded audit used `/usr/bin/python3`). The audit generates a fresh temporary schematic netlist; it checks logical membership, not trace completion. Mismatches exit nonzero even under `python3 -O`; validation uses explicit checks rather than removable assertions. `--project-dir` and `--repo-root` let regression tests check temporary copies without touching the working design. Inspect report contents: the CLI commands above can produce reports while returning success even with reported violations.

## Before routing and fabrication

1. Confirm the actual KB2040 revision, socket geometry and header stack height with a 1:1 print and samples.
2. Establish enclosure internal clearance, USB plug space and mounting points; revise the provisional outline.
3. Finalize exact harness connectors and orientation labels. Confirm every control against the existing wiring table.
4. Route all nets on F.Cu/B.Cu, provide ground distribution and review return paths. Assess optional filtering using measured analog noise.
5. Run ERC, DRC including unconnected items and schematic parity again. Review clearances, fabrication rules, silkscreen, actual part drawings and assembly access before generating manufacturing outputs.

No boards or parts have been ordered, and the active firmware has not been modified by this contribution.

## Audit regression checks

With KiCad's Python interpreter, run from the repository root:

```sh
python3 -m unittest discover -s tests -p test_pcb_audit.py -v
```

These integration tests accept the current design and deliberately corrupt a copied module coordinate and firmware pin assignment. Both mismatches must fail in normal and optimized Python modes. Without `pcbnew` or `kicad-cli`, these tests are skipped; a skipped test is not PCB validation.

Reviewed 2026-11-15: [Python assertion behavior](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) explains why `assert` is unsuitable as a mandatory audit check when optimized mode is permitted. KiCad check commands are documented in the [official CLI reference](https://docs.kicad.org/9.0/en/cli/cli.html).

## Header labels and harness checks

The front silkscreen now marks every control header pin: J1/J2/J3 show GND, A0/A1/A2 and +3V3; J4/J6/J7 show their digital input and GND; J5 shows D3, GND and D4. Numbers identify the carrier header pins, not the physical toggle's lug numbers. Labels reduce ambiguity but do not polarize the unkeyed connectors.

Before powering a completed assembly, verify each harness against the schematic with a continuity meter. The pot wiper must reach pin 2 and the other two pins must reach GND/+3V3. J5 pin 2 is common/GND; the switch itself must provide the specified center-off truth table. Do not use the label position to infer which way a cable housing is viewed. No harness or physical board has been tested here.

The project footprint table explicitly references the standard KiCad 9 connector library through `KICAD9_FOOTPRINT_DIR`, so checks do not depend on a preconfigured global footprint table. Install the standard KiCad libraries if that variable's directory is unavailable. Reviewed 2026-11-15 against the [KiCad PCB library documentation](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html).

## Paper-fit template and connector review (2026-11-16)

Open the [true-scale fit sheet](rev-a/previews/fit-template.svg) directly and print at **100% / actual size**, with fit-to-page disabled. GitHub's on-screen preview is not a scale reference. Verify the horizontal **100mm** and vertical **50mm** bars using a ruler; reject a print with either axis scaled incorrectly. This top view is not mirrored.

The sheet derives its provisional outline, all 44 drill centers/diameters and module F.Fab outline from the native board. It omits socket/header bodies, USB plug overhang, cable bends and mounting holes. The dashed module boundary is the bare PCB outline, not a clearance envelope. Paper fitting does not validate physical assembly or electrical operation. Follow the [connector fit review](CONNECTOR_REVIEW.md) for candidate parts, source drawings and unresolved stack decisions.

Regenerate after moving parts or editing the outline:

```sh
python3 hardware/pcb/rev-a/export_fit_template.py
```

Use KiCad's Python with `pcbnew`. The [exporter](rev-a/export_fit_template.py) records the source PCB SHA-256 in SVG metadata, uses millimeter page dimensions with a matching viewBox, and rejects unsupported outlines or a board too large for this sheet. No native design, pin assignment, routing or check report was changed by this paper template.

Desktop verification on 2026-11-16: all 44 SVG pad centers and drill radii match the native PCB, and page units/scale bars were checked numerically. The rendered sheet was visually inspected. All 26 existing desktop tests pass with KiCad Python. Fresh KiCad 9.0.2 checks report 0 ERC violations, 0 geometric DRC violations, 20 unconnected items and 0 schematic parity issues. These checks do not verify printer scaling or actual part/enclosure fit.

## Placement-independent audit (2026-11-18)

The module geometry check now uses KiCad's footprint-relative pad positions. Moving or rotating the complete front-side module no longer creates a false source-coordinate mismatch; moving one pad within the footprint still fails. Back-side mounting is rejected explicitly because this draft's mounting orientation has not been reviewed for a flipped module. This check does not approve a new placement: rerun DRC/parity, regenerate previews/fit sheets and review USB/enclosure clearance after moving parts.

Regression checks use temporary board copies at 90°, 180°, 270° and 37°, plus deliberately displaced pads and a flipped module. Both normal and optimized Python are checked. The committed board has not moved. Reviewed 2026-11-18 against the [official KiCad 9 PAD API](https://docs.kicad.org/doxygen-python-9.0/classpcbnew_1_1PAD.html), including inherited `GetFPRelativePosition()`.

## Fit-sheet USB direction (2026-11-19)

The fixed “USB faces left” annotation is replaced by a direction arrow transformed with the front-side KB2040 footprint. The module title and USB annotation move with it; the sheet rejects a missing, duplicate or back-side module rather than labeling an unreviewed mounting arrangement. The arrow indicates the USB end only: it is **not** the connector outline, plug overhang or a keepout.

The existing [pinned Adafruit board source](https://github.com/adafruit/Adafruit-KB2040-PCB/blob/b4160dcf4385ef2cc30e9652489328321720ee4b/Adafruit%20KB2040.brd) was rechecked on 2026-11-19: USB element X6 lies at Eagle y=8.89mm, on the module's west end. The exporter uses the existing 33.02 × 17.78mm bare-board convention. Rotation uses the [official KiCad 9 FOOTPRINT orientation API](https://docs.kicad.org/doxygen-python-9.0/classpcbnew_1_1FOOTPRINT.html); regression tests compare the arrow against the independently transformed module pad positions at 0°, 90°, 180°, 270° and 37°.

## Supported fit-sheet hole geometry (2026-11-19)

The sheet supports circular drilled holes only. The exporter now checks both drill dimensions and the KiCad drill-shape field before writing the SVG. Oblong slots or unequal drill dimensions raise an error instead of being silently shown as circles. A failed export leaves an existing sheet untouched; that old sheet is stale until a supported export succeeds. Always check the command exit status and source hash before using a sheet.

Tests check all 44 current pad centers/radii, physical SVG units, both scale bars, rotation behavior and rejection of slot geometry in temporary board copies. No native board or hole dimensions changed. API reference reviewed 2026-11-19: [KiCad 9 PAD drill size/shape methods](https://docs.kicad.org/doxygen-python-9.0/classpcbnew_1_1PAD.html). The regenerated current sheet and a rotated temporary example were visually inspected; no printer or physical fit check was performed.
