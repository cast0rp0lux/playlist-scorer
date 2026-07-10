from __future__ import annotations

import unittest

from app.bot.telegram_chunks import split_telegram_message


class TelegramChunkTests(unittest.TestCase):
    def test_short_message_returns_single_chunk(self) -> None:
        self.assertEqual(split_telegram_message("hello", limit=10), ["hello"])

    def test_prefers_newline_boundaries(self) -> None:
        chunks = split_telegram_message("alpha\nbeta\ngamma", limit=10)
        self.assertEqual(chunks, ["alpha\nbeta", "gamma"])

    def test_falls_back_to_spaces(self) -> None:
        chunks = split_telegram_message("alpha beta gamma", limit=10)
        self.assertEqual(chunks, ["alpha beta", "gamma"])


if __name__ == "__main__":
    unittest.main()
