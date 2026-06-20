from __future__ import annotations

import unittest

from app.core.engine import analyze_playlist
from app.core.ingestion.parser import parse_input
from app.core.models import Classification
from app.core.output.card import render_curatorial_card


class EngineTests(unittest.TestCase):
    def test_minimal_wave_playlist_scores_and_marks_descendant(self) -> None:
        request = parse_input(
            "\n".join(
                [
                    "Linear Movement - The Game",
                    "Absolute Body Control - Figures",
                    "Snowy Red - Euroshima",
                    "Molchat Doma - Sudno",
                ]
            ),
            playlist_name="Minimal Wave",
            pipeline="scene",
            target_scene="minimal wave",
            target_era="1980s",
        )
        result = analyze_playlist(request)
        classes = {track.artist: track.classification for track in result.tracks}
        self.assertEqual(classes["Linear Movement"], Classification.CORE)
        self.assertEqual(classes["Molchat Doma"], Classification.DESCENDANT)
        self.assertGreater(result.metrics.final_score, 70)

    def test_card_has_stable_end_marker(self) -> None:
        request = parse_input(
            "Unknown Artist - Unknown Song",
            playlist_name="Unknowns",
            pipeline="scene",
            target_scene="minimal wave",
            target_era="1980s",
        )
        card = render_curatorial_card(analyze_playlist(request))
        self.assertTrue(card.endswith("END"))
        self.assertIn("metadata_error", card)


if __name__ == "__main__":
    unittest.main()
