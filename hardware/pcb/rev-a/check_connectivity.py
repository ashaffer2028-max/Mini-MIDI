"""Audit source pin coordinates, firmware assignments and schematic/PCB net parity.

Run with the Python interpreter that provides KiCad's pcbnew module.
"""
from pathlib import Path
import ast
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    source = json.loads((ROOT / 'module-pin-map.json').read_text())
    board = pcbnew.LoadBoard(str(ROOT / 'mini-midi-carrier.kicad_pcb'))
    module = next(f for f in board.GetFootprints() if f.GetReference() == 'U1')
    padmap = {pad.GetNumber(): pad for pad in module.Pads()}
    assert len(padmap) == 26
    for pin in source['pins']:
        pad = padmap[str(pin['number'])]
        pos = pad.GetPosition() - module.GetPosition()
        assert abs(pcbnew.ToMM(pos.x) - pin['x_mm']) < .001
        assert abs(pcbnew.ToMM(pos.y) - pin['y_mm']) < .001
        if pin['net']:
            assert pad.GetNetname() == '/' + pin['net']

    expected = {'pot_deck_a': 'A0', 'pot_deck_b': 'A1', 'pot_crossfader': 'A2',
                'spst_filter': 'D2', 'dpdt_pin1': 'D3', 'dpdt_pin6': 'D4',
                'spst_d5': 'D5', 'spst_extra': 'D6'}
    found = {}
    for node in ast.walk(ast.parse((REPO / 'firmware/code.py').read_text())):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and node.value.args and isinstance(node.value.args[0], ast.Attribute)
                and isinstance(node.value.args[0].value, ast.Name)
                and node.value.args[0].value.id == 'board'):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in expected:
                    found[target.id] = node.value.args[0].attr
    assert found == expected, (found, expected)

    with tempfile.TemporaryDirectory() as tmp:
        netfile = Path(tmp) / 'netlist.xml'
        subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml',
                        '-o', str(netfile), str(ROOT / 'mini-midi-carrier.kicad_sch')],
                       check=True, capture_output=True)
        schematic = {n.attrib['name']: {(p.attrib['ref'], p.attrib['pin'])
                     for p in n.findall('node')} for n in ET.parse(netfile).findall('nets/net')}
    actual = {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetname():
                actual.setdefault(pad.GetNetname(), set()).add(
                    (footprint.GetReference(), pad.GetNumber()))
    assert schematic == actual, 'Schematic and board pad-to-net sets differ'
    print(json.dumps({'status': 'pass', 'module_pad_coordinates_checked': 26,
                      'firmware_assignments_checked': len(found),
                      'schematic_and_board_nets_checked': len(actual),
                      'routing_checked': False, 'physical_fit_checked': False}, indent=2))


if __name__ == '__main__':
    main()
