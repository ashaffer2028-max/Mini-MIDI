# Prototype wiring and sourcing

This wiring table is inferred from the existing firmware, **not verified against a physical schematic**. Disconnect USB before wiring. Use the KB2040's 3V rail for potentiometers and a common ground; do not feed RAW/USB 5V into analog inputs.

| KB2040 pin | Connection |
| --- | --- |
| A0 | Deck A potentiometer wiper |
| A1 | Deck B potentiometer wiper |
| A2 | Crossfader potentiometer wiper |
| 3V and GND | Opposite ends of each potentiometer track |
| D2 | Filter switch to GND when on |
| D3, D4 | EQ selector contacts; verify table below with continuity meter |
| D5 | Split-mode switch to GND when on |
| D6 | Assignable switch to GND when on |

Digital inputs use internal pull-ups: open means high; grounded means low. Swap a pot's outer track terminals if rotation is reversed. Check the component datasheet to identify the wiper.

## EQ selector electrical contract

| D3 | D4 | Firmware interpretation |
| --- | --- | --- |
| Grounded | Open | High EQ |
| Open | Open | Mid EQ |
| Open | Grounded | Low EQ |
| Grounded | Grounded | Mid EQ fallback |

A three-position switch must produce those states. A DPDT ON-OFF-ON can implement them using an appropriate pole, with its common grounded and two throws connected to D3/D4. Do not assume physical lug numbering or that a DPDT ON-ON-ON behaves the same. Verify all three positions before connecting the board; no powered rail is needed on the selector.

## Candidate BOM (not an order list)

Sources checked 2026-11-10. Prices, stock and fit are not guaranteed. The actual installed pot/switch models are not recorded in the repo.

| Qty | Item / specification | Candidate source | Check before ordering |
| --- | --- | --- | --- |
| 1 | Adafruit KB2040, product 5302 | [Adafruit](https://www.adafruit.com/product/5302) | USB port clearance, headers and board mounting |
| 3 | 10 kΩ linear rotary pot; product 562 is one prototype candidate | [Adafruit](https://www.adafruit.com/product/562) | Shaft/knob fit, bushing thread, body depth and pin spacing |
| 3 | Maintained SPST ON-OFF switch | [DigiKey](https://www.digikey.com/) / [Mouser](https://www.mouser.com/) | Panel opening and low-current contact suitability; no specific SKU selected |
| 1 | Three-position selector matching truth table above | [DigiKey](https://www.digikey.com/) / [Mouser](https://www.mouser.com/) | Contact diagram, not just “DPDT”; no specific SKU selected |
| 3 | Knobs matching selected pot shaft | [SparkFun](https://www.sparkfun.com/) / Adafruit | Shaft diameter, flat/spline and nearby switch clearance |
| 1 | USB data cable matching host and board | Adafruit / SparkFun | Data support, connector strain relief and bend radius |
| As needed | Wire, perfboard, insulation, mounting hardware | Adafruit / SparkFun | Enclosure space, solder accessibility and serviceability |

Use supplier datasheets to create a dimensioned BOM before changing CAD. A slide crossfader would require a different mechanical design; the current firmware assumes a third analog potentiometer and does not require rotary construction electrically.

Primary board reference: [KB2040 pinouts](https://learn.adafruit.com/adafruit-kb2040/pinouts).
