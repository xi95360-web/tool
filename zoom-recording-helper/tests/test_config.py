import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import config


class ConfigTests(unittest.TestCase):
    def test_defaults_contain_required_values(self):
        self.assertEqual(config.DEFAULT_CONFIG["obs_websocket_port"], 4455)
        self.assertEqual(config.DEFAULT_CONFIG["multi_output_device"], "Zoom Multi-Output")
        self.assertFalse(config.DEFAULT_CONFIG["transcribe"])

    def test_load_merges_user_values_and_expands_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text("obs_scene_name: My Scene\nrecording_directory: ~/Movies/Test\n", encoding="utf-8")
            with patch.object(config, "CONFIG_FILE", path):
                loaded = config.load_config()
            self.assertEqual(loaded["obs_scene_name"], "My Scene")
            self.assertTrue(loaded["recording_directory"].endswith("Movies/Test"))
            self.assertEqual(loaded["obs_websocket_port"], 4455)

    def test_bad_port_is_friendly_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text("obs_websocket_port: nope\n", encoding="utf-8")
            with patch.object(config, "CONFIG_FILE", path):
                with self.assertRaises(config.ConfigError):
                    config.load_config()


if __name__ == "__main__":
    unittest.main()
