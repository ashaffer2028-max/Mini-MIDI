"""Optional KiCad integration regressions; run with KiCad's Python interpreter."""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'hardware/pcb/rev-a'
SCRIPT = PROJECT / 'check_connectivity.py'
HAS_KICAD = importlib.util.find_spec('pcbnew') is not None and shutil.which('kicad-cli')


@unittest.skipUnless(HAS_KICAD, 'requires KiCad pcbnew and kicad-cli')
class PcbAuditTests(unittest.TestCase):
    def run_audit(self, project=PROJECT, repo=ROOT, optimized=False):
        cmd = [sys.executable] + (['-O'] if optimized else [])
        return subprocess.run(cmd + [str(SCRIPT), '--project-dir', str(project),
                              '--repo-root', str(repo)], capture_output=True, text=True)

    def test_current_design_passes_in_normal_and_optimized_modes(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.run_audit(optimized=optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)['status'], 'pass')

    def test_bad_source_coordinate_fails_including_optimized_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = pathlib.Path(tmp) / 'project'
            shutil.copytree(PROJECT, project)
            data = json.loads((project / 'module-pin-map.json').read_text())
            data['pins'][0]['x_mm'] += 1
            (project / 'module-pin-map.json').write_text(json.dumps(data))
            for optimized in (False, True):
                with self.subTest(optimized=optimized):
                    result = self.run_audit(project=project, optimized=optimized)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('differs from source coordinates', result.stderr)
                    self.assertNotIn('"status": "pass"', result.stdout)

    def test_firmware_pin_change_fails_including_optimized_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            (repo / 'firmware').mkdir()
            code = (ROOT / 'firmware/code.py').read_text()
            self.assertIn('analogio.AnalogIn(board.A0)', code)
            (repo / 'firmware/code.py').write_text(
                code.replace('analogio.AnalogIn(board.A0)', 'analogio.AnalogIn(board.A3)', 1))
            for optimized in (False, True):
                with self.subTest(optimized=optimized):
                    result = self.run_audit(repo=repo, optimized=optimized)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Firmware pin assignments differ', result.stderr)


if __name__ == '__main__':
    unittest.main()
