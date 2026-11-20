# Hardware files

| File or guide | Status |
| --- | --- |
| [Initial PCB model](pcb/README.md) | Editable KiCad schematic and unrouted placement draft; review required |
| [Prototype enclosure export](cad/prototype-enclosure.zip) | Early CAD concept; renamed from `Part Studio 1 - Part 1.zip` with unchanged contents |
| [Wiring and candidate parts](../docs/HARDWARE.md) | Inferred wiring, electrical requirements, sourcing and fit checks |
| [Carrier-to-panel harness](../docs/HARNESS.md) | Logical wiring diagram; physical assembly unverified |
| [Bench checklist](../docs/SETUP.md#bench-checklist--pending-physical-execution) | Physical validation still pending |

The ZIP is preserved as supplied. Component fit, panel dimensions and print readiness have not been verified. Check the selected parts and print a fit coupon before committing to an enclosure.

Put future CAD source files and exports in `hardware/cad/`, using names that identify the part and revision. Keep original editable source files alongside exports when available. Initial PCB files and their research notes live in `hardware/pcb/`; their provisional outline has not been fitted to this enclosure.

- [PCB paper-fit sheet](pcb/rev-a/previews/fit-template.svg) — print at actual size and verify both scale bars; provisional placement only.
- [Connector fit review](pcb/CONNECTOR_REVIEW.md) — exact header candidates, source drawings and unresolved module/socket stack.
