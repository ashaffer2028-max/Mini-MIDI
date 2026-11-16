# Control-header and socket fit review

Reviewed **2026-11-16**. All parts below are candidates, not confirmed installed hardware or an approved assembly BOM. The native PCB still uses generic KiCad header geometry.

## Exact control-header candidates

| References | Quantity | Candidate | Manufacturer evidence | Supplier |
| --- | --- | --- | --- | --- |
| J4, J6, J7 | 3 | Samtec TSW-102-07-G-S | [Exact 2-position product](https://www.samtec.com/products/tsw-102-07-g-s) | [DigiKey 612-TSW-102-07-G-S-ND](https://www.digikey.com/en/products/detail/samtec-inc/TSW-102-07-G-S/1101325) |
| J1, J2, J3, J5 | 4 | Samtec TSW-103-07-G-S | [Exact 3-position product](https://www.samtec.com/products/tsw-103-07-g-s) | [DigiKey 612-TSW-103-07-G-S-ND](https://www.digikey.com/en/products/detail/samtec-inc/TSW-103-07-G-S/1101324) |

Samtec specifies 2.54mm pitch, nominal 0.635mm square contacts, 5.84mm mating posts and 10.92mm overall contact length for these configurations. The [series drawing](https://suddendocs.samtec.com/prints/tsw-xxx-xx-xxx-x-xx-xxx-mkt.pdf) and [recommended footprint](https://suddendocs.samtec.com/prints/tsw-xxx-xx-x-x-xx-xxx-footprint.pdf) must be checked before substituting for the generic footprints. Link to these manufacturer drawings; no drawing or CAD model is redistributed here.

The PCB currently has 1.0mm nominal drills on these headers. A nominal 0.635mm square has a roughly 0.898mm diagonal, leaving only about 0.102mm diametral difference. That calculation is **not a tolerance analysis or hole-fit approval**: finished-hole tolerance, contact tolerance, plating and insertion allowance still need review. Do not shrink holes based on pitch alone. Body/courtyard clearance and the mating cable housing also remain unverified.

Stock distinction: the live DigiKey 2-position page displayed in-stock inventory when opened on 2026-11-16; no quantity is promised or reserved. The 3-position supplier listing was located, but its current inventory was not independently confirmed in this review. Socket inventory is unchecked. Recheck all stock and delivery at ordering.

## Module socket decision remains open

The earlier SSQ-113-03-G-S candidate has a supplier-listed 10.00mm tail below its 8.51mm insulation body ([DigiKey listing](https://www.digikey.com/en/products/detail/samtec-inc/SSQ-113-03-G-S/1111548), listing reviewed 2026-11-14). Such a long tail needs explicit underside clearance; it is not a low-profile choice merely because the pitch matches.

[Samtec SSQ-113-01-G-S](https://www.samtec.com/products/ssq-113-01-g-s) is a **shorter-tail alternative to investigate**, with 13 positions, 2.54mm pitch and a manufacturer-described 0.104in (about 2.64mm) tail. This changes the tail option, not a verified installed stack height. Neither socket is selected. Two socket strips also require two compatible male strips on the KB2040; those male strips and their insertion depth have not been selected or measured. A socket body height alone does not establish carrier-to-module separation.

## Evidence needed before freezing the layout

Use the [true-scale fit template](rev-a/previews/fit-template.svg) after verifying both scale bars with a ruler. Check the actual KB2040 hole centers and USB orientation, then offer up candidate socket/header samples without powering anything. Record actual part numbers, carrier thickness, underside tail protrusion, module underside clearance, USB plug overhang and cable bend space. Establish enclosure interior clearance and mounting points from an editable model or measurements; the existing OBJ's overall dimensions do not provide these.

Cable housings, contact/crimp tooling and retention are still unresolved. The unshrouded headers do not prevent reversal or a one-pin offset. Keep the existing pin-function labels and continuity-check each harness against the schematic before any powered test. Do not treat a successful paper fit as electrical or hardware validation.
