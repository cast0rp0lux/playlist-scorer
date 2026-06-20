from __future__ import annotations

import unittest

from app.core.ingestion.parser import parse_input
from app.core.utils.normalization import normalize_title


class ParserTests(unittest.TestCase):
    def test_parse_text_playlist(self) -> None:
        request = parse_input(
            "Linear Movement - The Game\nSnowy Red - Euroshima",
            playlist_name="Test",
            pipeline="scene",
        )
        self.assertEqual(len(request.tracks), 2)
        self.assertEqual(request.tracks[0].artist, "Linear Movement")
        self.assertEqual(request.tracks[0].title, "The Game")

    def test_parse_json_playlist(self) -> None:
        request = parse_input(
            {"name": "JSON Test", "tracks": [{"artist": "Snowy Red", "title": "Euroshima", "year": 1982}]},
            playlist_name="Fallback",
            pipeline="scene",
        )
        self.assertEqual(request.name, "JSON Test")
        self.assertEqual(request.tracks[0].year, 1982)

    def test_title_noise_is_removed(self) -> None:
        self.assertEqual(normalize_title("Song (2020 Remaster) [Official Video]"), "song")


if __name__ == "__main__":
    unittest.main()
