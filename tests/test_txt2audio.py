import sys, io

from unittest import TestCase
from unittest.mock import Mock, AsyncMock, patch
from subprocess import call
from pathlib import Path

import txt2audio


class TestTxt2Audio(TestCase):
    def setUp(self):
        Path('./hi.txt').write_text('hi')

    def tearDown(self):
        Path('./hi.txt').unlink(missing_ok=True)
        Path('./hi.mp3').unlink(missing_ok=True)

    @patch.object(txt2audio, 'BACK_END_TTS', 'PYTTS')
    @patch.object(sys, 'argv', ['txt2audio.py', 'hi.txt'])
    @patch('pyttsx3.init')
    def test_audio_generate_mp3_pytts(self, mock_init):
        mock_engine = mock_init()

        txt2audio.main()

        mp3 = str(Path('hi.mp3').resolve())

        mock_engine.save_to_file.assert_called_with('hi', mp3)
        mock_engine.runAndWait.assert_called()


    @patch.object(txt2audio, 'BACK_END_TTS', 'EDGE_TTS')
    @patch.object(sys, 'argv', ['txt2audio.py', 'hi.txt'])
    def test_audio_generate_mp3_edge(self):
        txt2audio.main()

        self.assertTrue(
            Path('hi.mp3').is_file()
        )


    @patch.object(sys, 'argv', ['txt2audio.py'])
    @patch('builtins.exit')
    def test_not_args(self, mock_exit):
        stdout = io.StringIO()
        sys.stdout = stdout

        txt2audio.main()

        sys.stdout = sys.__stdout__
        stdout = stdout.getvalue().strip()

        self.assertEqual(
            stdout,
            'Usage: txt2audio.py <input.txt>'
        )

        mock_exit.assert_called_with(1)


    @patch.object(sys, 'argv', ['txt2audio.py', 'not_found.txt'])
    def test_not_found_file_arg(self):
        with self.assertRaises(FileNotFoundError):
            txt2audio.main()
