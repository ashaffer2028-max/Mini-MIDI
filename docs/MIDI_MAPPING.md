# MIDI mapping

All messages are Control Change on **MIDI channel 1** (`out_channel=0` in the library). These are project assignments; map them manually in your DJ application.

| Mode / control | Deck A pot (A0) | Deck B pot (A1) |
| --- | --- | --- |
| D5 on: split mode, highest priority | CC 14, volume | CC 11, filter |
| D5 off, D2 on: filter mode | CC 10, filter | CC 11, filter |
| Both off, EQ high | CC 1 | CC 2 |
| Both off, EQ mid | CC 3 | CC 4 |
| Both off, EQ low | CC 5 | CC 6 |

A2 always sends CC 9 (crossfader). D6 sends CC 13 with 127 for on and 0 for off. Pot values span 0–127. Switching modes immediately sends the pot's current value to the new CC, so software parameters can jump; pickup/soft takeover is future work.

For wiring see [hardware details](HARDWARE.md); for installation and calibration see [setup](SETUP.md).
