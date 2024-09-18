"""
file: text_txt2audio.py
description: used to test txt conversion
"""
import sys
import os
import unittest
from unittest.mock import patch
from pathlib import Path

src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, src_path)

import txt2audio #pylint: disable=C0413

class TestTxt2Audio(unittest.TestCase):
    """Unit tests txt2audio.py"""
    def setUp(self):
        Path('./hi.txt').write_text('hi', encoding="UTF-8")

    def tearDown(self):
        Path('./hi.txt').unlink(missing_ok=True)
        Path('./hi.mp3').unlink(missing_ok=True)

    @patch.object(txt2audio, 'BACK_END_TTS', 'PYTTS')
    @patch.object(sys, 'argv', ['txt2audio.py', 'hi.txt'])
    @patch('pyttsx3.init')
    def test_audio_generate_mp3_pytts(self, mock_init):
        """Generate an example mp3 file and look for it using PYTTS"""
        mock_engine = mock_init()
        txt2audio.main()
        path_script = os.path.dirname(txt2audio.__file__)
        mp3 = os.path.join(path_script, 'hi.mp3')
        mock_engine.save_to_file.assert_called_with('hi', mp3)
        mock_engine.runAndWait.assert_called()

    @patch.object(txt2audio, 'BACK_END_TTS', 'EDGE_TTS')
    @patch.object(sys, 'argv', ['txt2audio.py', 'hi.txt'])
    def test_audio_generate_mp3_edge(self):
        """Generate an example mp3 file and look for it using EDGE_TTS"""
        txt2audio.main()
        path_script = os.path.dirname(txt2audio.__file__)
        mp3 = os.path.join(path_script, 'hi.mp3')
        self.assertTrue(Path(mp3).is_file())

    @patch.object(sys, 'argv', ['txt2audio.py'])
    def test_not_args(self):
        """Test failing in case of no input script"""
        with self.assertRaises(SystemExit), self.assertLogs() as cm:
            txt2audio.main()
            self.assertEqual(cm.output, ['ERROR:txt2audio:Usage: txt2audio.py <input.txt>'])

    @patch.object(sys, 'argv', ['txt2audio.py', 'not_found.txt'])
    def test_not_found_file_arg(self):
        """Test failing in case of wrong path"""
        with self.assertRaises(FileNotFoundError):
            txt2audio.main()

if __name__ == "__main__":
    unittest.main()
