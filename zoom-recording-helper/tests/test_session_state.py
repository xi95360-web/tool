import tempfile
import unittest
from pathlib import Path

from scripts.session import clear_session, load_session, save_session


class SessionStateTests(unittest.TestCase):
    def test_round_trip_and_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "current_session.json"
            state = {"status": "recording", "session_directory": "/tmp/example"}
            save_session(state, path)
            self.assertEqual(load_session(path), state)
            clear_session(path)
            self.assertIsNone(load_session(path))

    def test_missing_session_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_session(Path(tmp) / "missing.json"))


if __name__ == "__main__":
    unittest.main()
