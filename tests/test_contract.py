#!/usr/bin/env python3
"""Check the source boundary against the installed Omarchy stock lock."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = Path("/usr/share/omarchy/shell/plugins/lock")


class PluginContract(unittest.TestCase):
    def test_manifest_declares_one_lock_clone(self):
        manifest = json.loads((ROOT / "manifest.json").read_text())
        self.assertEqual(manifest["omarchy"]["clonedFrom"], "omarchy.lock")
        self.assertEqual(manifest["kinds"], ["service"])
        self.assertEqual(manifest["entryPoints"]["service"], "Service.qml")
        self.assertTrue(manifest["keepLoaded"])

    def test_service_preserves_installed_lock_code(self):
        self.assertEqual((ROOT / "Service.qml").read_text(),
                         (UPSTREAM / "Service.qml").read_text(),
                         "Service.qml drifted from the installed stock lock")

    def test_view_preserves_installed_lock_code(self):
        self.assertEqual((ROOT / "LockView.qml").read_text(),
                         (UPSTREAM / "LockView.qml").read_text(),
                         "LockView.qml drifted from the installed stock lock: "
                         "no GPU rain, stock background")


if __name__ == "__main__":
    unittest.main()
