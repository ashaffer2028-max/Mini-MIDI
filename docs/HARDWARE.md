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

## Pot and knob pair for enclosure planning

Reviewed 2026-11-11. These are **candidates**, not confirmed installed components or a verified fit in the supplied CAD.

| Candidate | Verified source details | Consequence for this build |
| --- | --- | --- |
| [Adafruit 562](https://www.adafruit.com/product/562), linked as P160KN-0QC15B10K | 10 kΩ linear; 16mm body; 0.2-inch terminal spacing | Electrically suitable as a 3.3V voltage divider; reserve space for the body and leads below the panel |
| [Adafruit 2046 red T18 knob](https://www.adafruit.com/product/2046) | Supplier explicitly pairs it with 562; 15mm base and 11mm top diameters | Candidate shaft match; do not substitute a D-shaft knob just because the diameter looks similar |

The supplier-linked [BI Technologies P160 datasheet](https://cdn-shop.adafruit.com/product-files/562/p160.pdf), pages 2–3, decodes the candidate as PC-pin style KN, no detent (`0`), type C shaft (6mm, 18 teeth), 15mm shaft length and linear taper (`B`). Its outline specifies an M7 × 0.75 bushing. Use the actual part drawing and sample when setting panel thickness and mounting-hole clearance; the bushing thread is not itself a hole-tolerance specification.

The datasheet gives nominal electrical travel of 260° versus mechanical travel of 300° ±10°. Allow for travel near the stops where output changes little. With no center detent, this candidate provides no tactile cue for neutral filter or crossfader center; assess that tradeoff before finalizing all three controls.

The 15mm knob base is not sufficient spacing by itself: the pot body is wider, and finger access, nearby toggles, solder joints and USB access need clearance. Print a panel test coupon and dry-fit samples before revising the whole enclosure. No dimensions have been measured on the existing prototype.

**Availability:** 562 retrievals disagreed on stock status, so availability is unconfirmed. The 2046 page showed stock when reviewed; quantity is not reserved and can change. Recheck both supplier pages before ordering. No purchases were made.
