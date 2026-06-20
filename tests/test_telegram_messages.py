from __future__ import annotations

import unittest

from app.bot.telegram_messages import analyze_text, build_reply, split_command


class TelegramMessagesTests(unittest.TestCase):
    def test_split_command_strips_bot_username(self) -> None:
        self.assertEqual(split_command("/score@PlaylistScorerBot Artist - Title"), ("/score", "Artist - Title"))

    def test_analyze_text_returns_card(self) -> None:
        card = analyze_text("Linear Movement - The Game", as_json=False)
        self.assertIn("PLAYLIST SCORER AUDIT", card)
        self.assertTrue(card.endswith("END"))

    def test_build_reply_handles_start(self) -> None:
        self.assertIn("Playlist Scorer", build_reply("/start"))


if __name__ == "__main__":
    unittest.main()
