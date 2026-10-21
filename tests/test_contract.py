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
        plugin = (ROOT / "Service.qml").read_text()
        self.assertEqual(plugin, (UPSTREAM / "Service.qml").read_text(),
                         "Service.qml drifted from the installed stock lock: "
                         "lock-only design keeps Service.qml identical to upstream, "
                         "rain lives only in LockView.qml")

    def test_view_changes_only_the_background(self):
        upstream = (UPSTREAM / "LockView.qml").read_text()
        original = '''    Image {
      id: wallpaper
      anchors.fill: parent
      source: root.loadBackground ? root.fileUrl(root.backgroundPath) : ""
      fillMode: Image.PreserveAspectCrop
      asynchronous: true
      cache: false
      sourceSize.width: width
      sourceSize.height: height
    }

    MultiEffect {
      anchors.fill: wallpaper
      source: wallpaper
      autoPaddingEnabled: false
      blurEnabled: root.loadBackground && wallpaper.status === Image.Ready
      blur: 1.0
      blurMax: 128
      blurMultiplier: 1.25
      contrast: -0.08
    }'''
        replacement = '''    MatrixRain {
      anchors.fill: parent
      running: root.loadBackground
      onRunningChanged: if (running) restart()
    }'''
        self.assertEqual(upstream.count(original), 1)
        expected = upstream.replace(original, replacement, 1)
        expected = expected.replace("    color: Commons.Color.background\n",
                                    '    color: "black"\n', 1)
        self.assertEqual((ROOT / "LockView.qml").read_text(), expected,
                         "LockView.qml drifted from the installed stock lock: "
                         "port upstream first, then keep only the MatrixRain background")

    def test_assets_exist(self):
        for name in ("glyphs.png", "matrix.frag.qsb", "tools/matrix.frag"):
            self.assertGreater((ROOT / name).stat().st_size, 0)

    def test_rain_holds_one_second_before_start(self):
        rain = (ROOT / "MatrixRain.qml").read_text()
        self.assertIn("property int startDelayMs: 1000", rain)
        self.assertIn("visible: !root.delayingStart", rain)
        self.assertIn("root.running && !root.delayingStart", rain)
        self.assertIn("Component.onCompleted: if (root.running", rain)
        for name in ("LockView.qml",):
            self.assertIn("onRunningChanged: if (running) restart()",
                          (ROOT / name).read_text(), name)


if __name__ == "__main__":
    unittest.main()
