import sys
import unittest
from pathlib import Path

from app import ROOT, build_command


class AppTests(unittest.TestCase):
    def test_build_command_includes_requested_inputs(self):
        command = build_command(
            sys.executable, "panoramas", "map.jpg", "out", "detector.pt", "classifier.pt",
            "0.25", "0", "poses.csv", "ranges.json", True,
        )
        self.assertEqual(command[0], sys.executable)
        self.assertEqual(Path(command[1]), ROOT / "demo.py")
        self.assertIn("--pose-csv", command)
        self.assertIn("poses.csv", command)
        self.assertIn("--range-manifest", command)
        self.assertIn("--export-six-faces", command)

    def test_build_command_omits_optional_inputs(self):
        command = build_command(sys.executable, "panoramas", "map.jpg", "out", "detector.pt", "classifier.pt", "0.25", "1")
        self.assertNotIn("--pose-csv", command)
        self.assertNotIn("--range-manifest", command)


if __name__ == "__main__":
    unittest.main()
