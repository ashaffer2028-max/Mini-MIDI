"""KiCad integration tests for paper geometry, not physical fit validation."""
import hashlib
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'hardware/pcb/rev-a'
spec = importlib.util.spec_from_file_location('fit_template', PROJECT / 'export_fit_template.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
HAS_PCBNEW = importlib.util.find_spec('pcbnew') is not None
NS = {'s': exporter.NS}


@unittest.skipUnless(HAS_PCBNEW, 'requires KiCad pcbnew')
class FitTemplateTests(unittest.TestCase):
    def setUp(self):
        import pcbnew
        self.p = pcbnew
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.board_path = Path(self.temp.name) / 'board.kicad_pcb'
        self.output = Path(self.temp.name) / 'fit.svg'
        self.board = pcbnew.LoadBoard(str(PROJECT / 'mini-midi-carrier.kicad_pcb'))
        self.module = next(f for f in self.board.GetFootprints() if f.GetReference() == 'U1')

    def export(self):
        self.p.SaveBoard(str(self.board_path), self.board)
        exporter.export(self.board_path, self.output)
        return ET.parse(self.output).getroot()

    def test_physical_scale_and_all_pad_centers_match_native_board(self):
        root = self.export()
        self.assertEqual((root.get('width'), root.get('height'), root.get('viewBox')),
                         ('190mm', '165mm', '0 0 190 165'))
        circles = {(c.get('data-ref'), c.get('data-pad')): c
                   for c in root.findall('s:circle', NS)}
        expected = {(f.GetReference(), q.GetNumber()): q
                    for f in self.board.GetFootprints() for q in f.Pads()}
        self.assertEqual(set(circles), set(expected))
        self.assertEqual(len(circles), 44)
        for key, pad in expected.items():
            circle = circles[key]
            self.assertAlmostEqual(float(circle.get('cx')), self.p.ToMM(pad.GetPosition().x) + 10, places=4)
            self.assertAlmostEqual(float(circle.get('cy')), self.p.ToMM(pad.GetPosition().y) + 20, places=4)
            self.assertAlmostEqual(float(circle.get('r')), self.p.ToMM(pad.GetDrillSize().x) / 2, places=4)
        for axis, length in (('x', 100), ('y', 50)):
            bar = root.find("s:line[@id='scale-{}-{}mm']".format(axis, length), NS)
            self.assertEqual(float(bar.get(axis + '2')) - float(bar.get(axis + '1')), length)
        self.assertIn(hashlib.sha256(self.board_path.read_bytes()).hexdigest(),
                      root.find('s:metadata', NS).text)

    def test_usb_arrow_tracks_moved_rotated_module_pad_geometry(self):
        self.module.SetPosition(self.p.VECTOR2I(self.p.FromMM(65), self.p.FromMM(50)))
        for angle in (0, 90, 180, 270, 37):
            with self.subTest(angle=angle):
                self.module.SetOrientationDegrees(angle)
                root = self.export()
                arrow = root.find("s:line[@id='module-usb-direction']", NS)
                dx = float(arrow.get('x2')) - float(arrow.get('x1'))
                dy = float(arrow.get('y2')) - float(arrow.get('y1'))
                self.assertAlmostEqual(math.hypot(dx, dy), 6, places=5)
                pads = {q.GetNumber(): q for q in self.module.Pads()}
                # Top-row pad 14 -> 26 points toward the actual USB end.
                direction = pads['26'].GetPosition() - pads['14'].GetPosition()
                px, py = self.p.ToMM(direction.x), self.p.ToMM(direction.y)
                self.assertAlmostEqual(dx * py - dy * px, 0, places=4)
                self.assertGreater(dx * px + dy * py, 0)
                self.assertNotIn('USB faces left', self.output.read_text())

    def test_slot_drills_are_rejected_without_overwriting_existing_sheet(self):
        pad = next(iter(self.module.Pads()))
        self.output.write_text('existing reviewed sheet')
        for shape, size in ((self.p.PAD_DRILL_SHAPE_OBLONG, (1, 2)),
                            (self.p.PAD_DRILL_SHAPE_CIRCLE, (1, 2))):
            with self.subTest(shape=shape):
                pad.SetDrillShape(shape)
                pad.SetDrillSize(self.p.VECTOR2I(*[self.p.FromMM(v) for v in size]))
                self.p.SaveBoard(str(self.board_path), self.board)
                with self.assertRaisesRegex(ValueError, 'requires circular drills'):
                    exporter.export(self.board_path, self.output)
                self.assertEqual(self.output.read_text(), 'existing reviewed sheet')


if __name__ == '__main__':
    unittest.main()
