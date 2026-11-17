# Capture and review endpoint calibration

Reviewed **2026-11-17**. This workflow turns real stationary diagnostic readings into **candidate** per-pot bounds. No prototype readings or completed hardware tests are supplied. The analyzer runs on desktop Python 3 and never edits the controller or contacts the board.

## Collect two separate logs

1. Follow the [bench tool backup/deployment steps](../tools/README.md#run-on-the-board). Set `CSV_OUTPUT = True` in the diagnostic before deploying it as `CIRCUITPY/code.py`.
2. Put all three pots at their low-output stops and let readings settle. Use the serial terminal's logging feature to capture a header `control,min,max,mean,span`, followed by several **complete A0/A1/A2 windows**, as `low.csv`. Start with the pots already stationary; do not include a moving sweep or settling windows. If starting a new capture after the header has passed, copy the header exactly above the captured rows.
3. Stop that capture, move to the high-output stops and settle, then capture `high.csv` in the same format with its own header. Keep center/noise/sweep logs separate. Each file needs at least two full windows to be accepted; that minimum is a format safeguard, not statistical confidence.
4. Keep `#` diagnostic lines if desired. Exclude REPL prompts, boot banners and terminal control characters from the capture. Unexpected or partial CSV rows are rejected rather than silently discarded. Preserve original logs; don't change measured numbers to make a file pass.
5. Record the date, actual board revision, CircuitPython version, diagnostic commit, wiring/component changes, control positions and capture procedure alongside the logs. File names alone do not establish that the readings came from hardware. Do not upload personal serial-port paths or unrelated terminal output.

Run from the repository root on the **computer**, not CircuitPython:

```sh
python tools/summarize_calibration.py --low low.csv --high high.csv
```

The JSON report includes source-file SHA-256 hashes, accepted window counts, largest within-window raw span and suggested bounds for `deck_a`/A0, `deck_b`/A1 and `crossfader`/A2. Standard-output redirection can save it locally if desired. No firmware write operation is provided.

## Interpret the result before applying it

For each pot, the candidate minimum is the **largest maximum across the low-stop windows**. The candidate maximum is the **smallest minimum across the high-stop windows**. This implements the existing [inner endpoint-bound procedure](SETUP.md#measure-and-enter-per-pot-bounds) so observed endpoint noise is clamped. It does not extrapolate, add arbitrary margins, trim outliers or reverse a pot.

The tool rejects malformed columns, incomplete/reordered windows, missing controls, nonfinite means, values outside 0–65535, inconsistent min/max/mean/span statistics, and overlapping or reversed stop envelopes. A syntactically valid but moving or incorrectly labeled capture can still yield bad candidates. Narrow spans are reported numerically, not diagnosed as healthy; inspect wiring and remeasure before using suspicious results. Large differences between stationary windows can indicate drift, movement or capture mistakes.

Review the logs, then manually enter each approved pair in `pot_ranges` in `firmware/code.py`. Restore the controller program and follow the existing endpoint, center, sweep and MIDI-monitor checks. Save the final approved bounds with the real test record. Endpoint calculations do not validate ADC linearity, detent alignment, physical latency, USB behavior or idle MIDI jitter after EMA filtering.

## Sources and hardware status

- [Official CircuitPython analogio API](https://docs.circuitpython.org/en/stable/shared-bindings/analogio/index.html#analogio.AnalogIn.value), reviewed 2026-11-17: readings use the 0–65535 API scale even with a lower-resolution ADC. This is not 16-bit physical accuracy; the documentation also cautions that endpoint voltage scaling may be nonlinear.
- [Official KB2040 pinouts](https://learn.adafruit.com/adafruit-kb2040/pinouts), reviewed 2026-11-17: retain the existing A0/A1/A2 wiring and 3V pot supply. No new pin assignment or component is required for CSV capture.
- [Adafruit KB2040 product 5302](https://www.adafruit.com/product/5302), supplier page reviewed 2026-11-17: displayed in stock at review, with no reservation or delivery guarantee. This is the project's existing module design, not evidence of the user's installed revision. Other candidate-part inventories were not checked in this review; the [hardware guide](HARDWARE.md) retains their candidate status.

Desktop regressions use explicitly synthetic fixture values. They verify calculations and rejection paths, not physical calibration. The PCB and its unresolved fit/routing work are unchanged.
