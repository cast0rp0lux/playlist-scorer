from __future__ import annotations

import unittest

from app.bot.simple_telegram_bot import analyze_text, split_command


class SimpleTelegramBotTests(unittest.TestCase):
    def test_split_command_strips_bot_username(self) -> None:
        self.assertEqual(split_command("/score@PlaylistScorerBot Artist - Title"), ("/score", "Artist - Title"))

    def test_analyze_text_returns_card(self) -> None:
        card = analyze_text("Linear Movement - The Game", as_json=False)
        self.assertIn("PLAYLIST SCORER AUDIT", card)
        self.assertTrue(card.endswith("END"))


if __name__ == "__main__":
    unittest.main()
