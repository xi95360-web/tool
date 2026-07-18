import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts.file_manager import meeting_filename, organize_recording, session_directory


class FileNamingTests(unittest.TestCase):
    def test_session_directory_format(self):
        root = Path("/tmp/recordings")
        value = session_directory(root, datetime(2026, 7, 15, 14, 30))
        self.assertEqual(value.name, "2026-07-15_14-30_Zoom")

    def test_meeting_filename(self):
        value = meeting_filename(datetime(2026, 7, 15, 14, 30), ".mkv")
        self.assertEqual(value, "2026-07-15_14-30_Zoom_Meeting.mkv")

    def test_organize_moves_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "obs-output.mkv"
            source.write_bytes(b"recording")
            target_dir = root / "session"
            target = organize_recording(source, target_dir, datetime(2026, 7, 15, 14, 30))
            self.assertTrue(target.exists())
            self.assertFalse(source.exists())
            self.assertEqual(target.name, "2026-07-15_14-30_Zoom_Meeting.mkv")


if __name__ == "__main__":
    unittest.main()
