"""Audit pin geometry, firmware assignments and schematic/PCB net membership.

Use a Python interpreter with KiCad's pcbnew module. This does not verify routing.
"""
from pathlib import Path
import argparse
import ast
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


class AuditError(ValueError):
    """A design mismatch that must fail even when Python uses -O."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


def audit(project_dir, repo_root):
    import pcbnew

    source = json.loads((project_dir / 'module-pin-map.json').read_text())
    board = pcbnew.LoadBoard(str(project_dir / 'mini-midi-carrier.kicad_pcb'))
    modules = [f for f in board.GetFootprints() if f.GetReference() == 'U1']
    require(len(modules) == 1, 'Expected exactly one module footprint U1')
    module = modules[0]
    require(module.GetLayer() == pcbnew.F_Cu,
            'Module U1 must remain on the front side; flipped mounting is not reviewed')
    pads = list(module.Pads())
    padmap = {pad.GetNumber(): pad for pad in pads}
    numbers = {str(pin['number']) for pin in source['pins']}
    expected_numbers = {str(i) for i in range(1, 27)}
    require(len(pads) == len(source['pins']) == 26 and
            set(padmap) == numbers == expected_numbers,
            'Module and source map must each contain pads 1 through 26 exactly once')
    for pin in source['pins']:
        number = str(pin['number'])
        pad = padmap[number]
        # Compare footprint-local geometry, independent of placement/rotation.
        pos = pad.GetFPRelativePosition()
        require(abs(pcbnew.ToMM(pos.x) - pin['x_mm']) < .001 and
                abs(pcbnew.ToMM(pos.y) - pin['y_mm']) < .001,
                'Module pad {} differs from source coordinates'.format(number))
        if pin['net']:
            require(pad.GetNetname() == '/' + pin['net'],
                    'Module pad {} has the wrong net'.format(number))

    expected = {'pot_deck_a': 'A0', 'pot_deck_b': 'A1', 'pot_crossfader': 'A2',
                'spst_filter': 'D2', 'dpdt_pin1': 'D3', 'dpdt_pin6': 'D4',
                'spst_d5': 'D5', 'spst_extra': 'D6'}
    found = {}
    for node in ast.walk(ast.parse((repo_root / 'firmware/code.py').read_text())):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and node.value.args and isinstance(node.value.args[0], ast.Attribute)
                and isinstance(node.value.args[0].value, ast.Name)
                and node.value.args[0].value.id == 'board'):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in expected:
                    found[target.id] = node.value.args[0].attr
    require(found == expected, 'Firmware pin assignments differ: {!r}'.format(found))

    with tempfile.TemporaryDirectory() as tmp:
        netfile = Path(tmp) / 'netlist.xml'
        subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml',
                        '-o', str(netfile), str(project_dir / 'mini-midi-carrier.kicad_sch')],
                       check=True, capture_output=True)
        schematic = {n.attrib['name']: {(p.attrib['ref'], p.attrib['pin'])
                     for p in n.findall('node')} for n in ET.parse(netfile).findall('nets/net')}
    actual = {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetname():
                actual.setdefault(pad.GetNetname(), set()).add(
                    (footprint.GetReference(), pad.GetNumber()))
    require(schematic == actual, 'Schematic and board pad-to-net sets differ')
    return {'status': 'pass', 'module_pad_coordinates_checked': len(pads),
            'firmware_assignments_checked': len(found),
            'schematic_and_board_nets_checked': len(actual),
            'routing_checked': False, 'physical_fit_checked': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-dir', type=Path, default=ROOT)
    parser.add_argument('--repo-root', type=Path, default=REPO)
    args = parser.parse_args()
    try:
        result = audit(args.project_dir.resolve(), args.repo_root.resolve())
    except (AuditError, OSError, KeyError, ValueError, StopIteration,
            subprocess.CalledProcessError) as error:
        parser.exit(1, 'Connectivity audit failed: {}\n'.format(error))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
