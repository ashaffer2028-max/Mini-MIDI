"""Export a true-scale, top-view SVG from the current KiCad placement.

Run using KiCad's Python. This is a paper-fit aid, not manufacturing output.
"""
from pathlib import Path
import argparse
import hashlib
import math
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def export(board_path, output):
    import pcbnew as p

    board = p.LoadBoard(str(board_path))
    edges = [d for d in board.GetDrawings() if d.GetLayer() == p.Edge_Cuts]
    if not edges or any(not isinstance(d, p.PCB_SHAPE) or
                        d.GetShape() != p.SHAPE_T_SEGMENT for d in edges):
        raise ValueError('Template exporter currently requires straight outline segments')
    points = [v for d in edges for v in (d.GetStart(), d.GetEnd())]
    xmin, ymin = min(v.x for v in points), min(v.y for v in points)
    xmax, ymax = max(v.x for v in points), max(v.y for v in points)
    width, height = p.ToMM(xmax - xmin), p.ToMM(ymax - ymin)
    if width > 110 or height > 65:
        raise ValueError('Outline exceeds this print sheet; revise page layout first')
    # A top-view sheet cannot represent an unreviewed back-side module.
    modules = [f for f in board.GetFootprints() if f.GetReference() == 'U1']
    if len(modules) != 1 or modules[0].GetLayer() != p.F_Cu:
        raise ValueError('Expected one front-side KB2040 module U1')
    svg = ET.Element(f'{{{NS}}}svg', width='190mm', height='165mm',
                     viewBox='0 0 190 165')
    ET.SubElement(svg, f'{{{NS}}}title').text = 'Mini-MIDI paper-fit template, top view'
    ET.SubElement(svg, f'{{{NS}}}metadata').text = (
        'Source PCB SHA-256: ' + hashlib.sha256(board_path.read_bytes()).hexdigest())

    def element(tag, **attrs):
        return ET.SubElement(svg, f'{{{NS}}}{tag}', {k: str(v) for k, v in attrs.items()})

    def text(x, y, value, size=3):
        element('text', x=x, y=y, fill='black', **{'font-family': 'sans-serif',
                'font-size': size}).text = value

    def xy(v):
        return p.ToMM(v.x - xmin) + 30, p.ToMM(v.y - ymin) + 40

    def line(x1, y1, x2, y2, **extra):
        return element('line', x1=x1, y1=y1, x2=x2, y2=y2,
                       stroke='black', **{'stroke-width': '.2'}, **extra)

    defs = ET.SubElement(svg, f'{{{NS}}}defs')
    marker = ET.SubElement(defs, f'{{{NS}}}marker', id='usb-arrow',
                           markerWidth='4', markerHeight='4', refX='3', refY='2',
                           orient='auto', markerUnits='userSpaceOnUse')
    ET.SubElement(marker, f'{{{NS}}}path', d='M 0,0 L 3,2 L 0,4',
                  fill='none', stroke='black', **{'stroke-width': '.3'})

    text(15, 12, 'Mini-MIDI carrier | PAPER FIT ONLY', 4)
    text(15, 19, 'Top view; print at 100% / actual size. Disable fit-to-page.')
    text(15, 25, 'Measure BOTH scale bars before comparing parts. No drilling or fabrication.')
    text(30, 35, f'Provisional outline: {width:g} x {height:g} mm')
    for d in edges:
        x1, y1 = xy(d.GetStart())
        x2, y2 = xy(d.GetEnd())
        line(x1, y1, x2, y2)

    count = 0
    for f in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        ref = f.GetReference()
        fx, fy = xy(f.GetPosition())
        if ref == 'U1':
            for d in f.GraphicalItems():
                if isinstance(d, p.PCB_SHAPE) and d.GetLayer() == p.F_Fab:
                    if d.GetShape() != p.SHAPE_T_SEGMENT:
                        raise ValueError('Unsupported module fabrication shape')
                    line(*xy(d.GetStart()), *xy(d.GetEnd()), **{'stroke-dasharray': '1,1'})
            # Source-map convention: module-local USB edge is x=0, y=8.89.
            # KiCad positive angles rotate counterclockwise on the screen.
            angle = math.radians(f.GetOrientationDegrees())

            def module_xy(x, y):
                return (fx + x * math.cos(angle) + y * math.sin(angle),
                        fy - x * math.sin(angle) + y * math.cos(angle))

            cx, cy = module_xy(16.51, 8.89)
            title = element('text', x=cx, y=cy, fill='black',
                            **{'font-family': 'sans-serif', 'font-size': '2.4',
                               'text-anchor': 'middle'})
            title.text = 'U1 KB2040'
            sx, sy = module_xy(4, 8.89)
            ex, ey = module_xy(-2, 8.89)
            line(sx, sy, ex, ey, **{'id': 'module-usb-direction',
                                  'marker-end': 'url(#usb-arrow)'})
            tx, ty = module_xy(6, 5.5)
            text(tx, ty, 'USB', 2.2)
        else:
            text(fx + 2.5, fy, ref, 2.4)
        for pad in sorted(f.Pads(), key=lambda pad: int(pad.GetNumber())):
            x, y = xy(pad.GetPosition())
            radius = p.ToMM(pad.GetDrillSize().x) / 2
            if radius <= 0:
                raise ValueError('Template requires through-hole pads')
            element('circle', cx=f'{x:.4f}', cy=f'{y:.4f}', r=f'{radius:.4f}',
                    fill='white', stroke='black', **{'stroke-width': '.15',
                    'data-ref': ref, 'data-pad': pad.GetNumber()})
            if ref != 'U1' or pad.GetNumber() in ('1', '13', '14', '26'):
                text(x - 3 if ref != 'U1' else x - .6,
                     y + .6 if ref != 'U1' else y - 1.2, pad.GetNumber(), 1.7)
            count += 1
    text(30, 111, 'Circles = draft drill diameters; dashed box = module PCB outline.', 2.7)
    text(30, 116, 'Connector bodies, USB plug, cable bends and mounting points are NOT modeled.', 2.7)
    line(30, 130, 130, 130, **{'id': 'scale-x-100mm'})
    for x in range(30, 131, 10):
        line(x, 128, x, 132)
    text(30, 138, '100 mm horizontal scale')
    line(160, 45, 160, 95, **{'id': 'scale-y-50mm'})
    for y in range(45, 96, 10):
        line(158, y, 162, y)
    text(146, 103, '50 mm vertical', 2.5)
    text(15, 150, 'UNROUTED DRAFT | No physical fit or electrical test has been performed.', 2.8)
    text(15, 156, f'{count} pad centers exported from the native PCB; regenerate after placement edits.', 2.8)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(svg)
    ET.ElementTree(svg).write(output, encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', type=Path, default=ROOT / 'mini-midi-carrier.kicad_pcb')
    parser.add_argument('--output', type=Path, default=ROOT / 'previews/fit-template.svg')
    args = parser.parse_args()
    export(args.board, args.output)


if __name__ == '__main__':
    main()
