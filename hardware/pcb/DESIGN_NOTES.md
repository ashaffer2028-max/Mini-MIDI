# Mini-MIDI carrier architecture — revision A

Research and draft review date: **2026-11-14**. This is a socketed **KB2040 carrier**, preserving the current firmware pin assignments. It is not a new RP2040 or USB implementation. The module supplies USB, regulation and processing; the carrier distributes its 3.3V rail, ground and eight control signals.

## Electrical contract

| Firmware input | Carrier module pad | Control connector |
| --- | --- | --- |
| A0, deck A | U1.18 (upstream JP1.5) | J1.2 |
| A1, deck B | U1.19 (JP1.6) | J2.2 |
| A2, crossfader | U1.20 (JP1.7) | J3.2 |
| D2, filter | U1.6 (JP2.6) | J4.1 |
| D3, EQ high contact | U1.7 (JP2.7) | J5.1 |
| D4, EQ low contact | U1.8 (JP2.8) | J5.3 |
| D5, split | U1.9 (JP2.9) | J6.1 |
| D6, assignable | U1.10 (JP2.10) | J7.1 |
| 3.3V supply | U1.22 (JP1.9) | J1.3, J2.3, J3.3 |
| Ground | U1.4, U1.5, U1.24 | J1–J7 ground terminals |

J1/J2/J3 use **1=GND, 2=wiper, 3=3.3V**. J4/J6/J7 use **1=signal, 2=GND**. J5 uses **1=D3, 2=GND, 3=D4**; connect its common to the selector common, and its throws to the correct switch terminals. J5 numbering is a connector convention, not the physical switch's lug numbering. Refer to the [selector guide](../../docs/HARDWARE.md#specific-eq-selector-candidate).

Spare module pins are marked NC on the carrier, including RAW and USB D+/D−. Their module functions still exist; they simply have no carrier traces. Do not power pots from RAW or attach a second supply to the 3.3V rail. All three SPST controls and both EQ contacts rely on the existing firmware input pull-ups. No new filters or component values have been inserted without measured noise data.

## Geometry and footprint choices

The upstream Eagle board at commit `b4160dcf4385ef2cc30e9652489328321720ee4b` has a 33.02 × 17.78mm board outline, 2.54mm drilled-pad pitch and 15.24mm row spacing. Its drilled pads, not the additional castellated pads, were used to reconstruct the carrier footprint. [module-pin-map.json](rev-a/module-pin-map.json) records all 26 pad centers, functions and source header/pad IDs. The custom footprint uses 1.0mm drills and 1.8mm pads as a **draft choice**, requiring review against the selected socket leads and fabrication capabilities.

Top-view convention: module USB points west. Carrier pad numbers 1–13 follow upstream JP2.1–13; pads 14–26 follow JP1.1–13. Do not substitute a generic Pro Micro footprint or assume it has the same pad count.

The enclosure ZIP was opened: it contains an Onshape OBJ/MTL mesh export, not an editable solid model. The OBJ declares meters; vertex bounds convert to **254 × 152.4 × 35.56mm**. Those are overall mesh bounds, not verified interior clearance or a mounting envelope. No standoff pattern was established. The **90 × 60mm** carrier outline and connector placements are provisional, with no mounting holes yet. It has not been registered to the enclosure mesh.

Controls remain panel-mounted and wired to generic 2.54mm headers. This avoids guessing pot and toggle PCB footprints before the actual parts and panel positions are confirmed. The USB plug envelope, underside module clearance, socket stack height, cable bends and retention must be checked on samples. No keepout or clearance certification is implied by a rectangular module outline.

## Parts to investigate — not a release BOM

| Item | Quantity | Candidate/source | Unresolved checks |
| --- | --- | --- | --- |
| Existing KB2040 module | 1 | [Adafruit 5302](https://www.adafruit.com/product/5302) | Confirm purchased revision against pinned board source |
| 1×13, 2.54mm socket row | 2 | [Samtec SSQ-113-03-G-S at DigiKey](https://www.digikey.com/en/products/detail/samtec-inc/SSQ-113-03-G-S/1111548) | Candidate only: long posts/height, hole fit and module mating need drawing/sample review |
| 1×3 control header | 4 | [Samtec TSW-103-07-G-S at DigiKey](https://www.digikey.com/en/products/detail/samtec-inc/TSW-103-07-G-S/1101324) | Candidate only: compare exact drawing to generic KiCad pads and choose mating harness |
| 1×2 control header | 3 | Generic KiCad geometry; no SKU selected | Select exact header and mating connector before release |

The supplier listings confirm the first socket's 13 positions and the header's three positions at 2.54mm pitch. They do not certify this layout. Prices, stock and delivery are intentionally not promised; recheck at ordering. The unkeyed headers can be miswired; consider polarized connectors after the harness and space requirements are known.

## Sources and attribution

- [Adafruit KB2040 board source, pinned commit](https://github.com/adafruit/Adafruit-KB2040-PCB/tree/b4160dcf4385ef2cc30e9652489328321720ee4b): `Adafruit KB2040.brd`, elements JP1/JP2, `1X13_CASTEL` drilled pads and signal contactrefs. Original board designed by Limor Fried/Ladyada for Adafruit Industries; upstream source is [CC BY-SA 3.0](https://github.com/adafruit/Adafruit-KB2040-PCB/blob/b4160dcf4385ef2cc30e9652489328321720ee4b/license.txt). The carrier is newly drawn using these dimensional/pin facts; upstream circuitry is not copied into it.
- [Official KB2040 pinouts](https://learn.adafruit.com/adafruit-kb2040/pinouts): cross-check power and pin functions. Use the pinned board geometry rather than rounded shop dimensions for pad locations.
- [KiCad 9 CLI documentation](https://docs.kicad.org/9.0/en/cli/cli.html): ERC, DRC, netlist and SVG commands. Installed editor/CLI version: 9.0.2.
- Generic connector footprints: installed KiCad `Connector_PinHeader_2.54mm` library, attributed to the KiCad library contributors; [library license and design exception](https://www.kicad.org/libraries/license/).
- Supplier links in the candidate table were reviewed on 2026-11-14. No stock reservation or purchase was made.
