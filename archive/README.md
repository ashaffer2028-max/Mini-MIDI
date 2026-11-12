# Historical firmware

These snapshots retain their original file contents. They are historical references; use the current files in [firmware/](../firmware/) for development and installation.

| Original path | Current path |
| --- | --- |
| `proto1 code` | [firmware/prototype-01.py](firmware/prototype-01.py) |
| `code revision 1` | [firmware/revision-01.py](firmware/revision-01.py) |

Both snapshots include the old D2 three-second reboot behavior. Their comments describe the original implementation and may include unverified performance claims. The added `.py` extensions make them readable as Python source without altering their bytes.

Changes to active firmware belong in `firmware/`; preserve these snapshots for comparison.
