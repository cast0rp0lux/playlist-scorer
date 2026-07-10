from __future__ import annotations

import unittest

from app.api.telegram_security import is_valid_webhook_secret


class TelegramSecurityTests(unittest.TestCase):
    def test_valid_webhook_secret_characters(self) -> None:
        self.assertTrue(is_valid_webhook_secret("abcXYZ_123-456"))

    def test_rejects_secret_with_unallowed_characters(self) -> None:
        self.assertFalse(is_valid_webhook_secret("abc/123"))
        self.assertFalse(is_valid_webhook_secret("abc:123"))

    def test_rejects_empty_or_too_long_secret(self) -> None:
        self.assertFalse(is_valid_webhook_secret(""))
        self.assertFalse(is_valid_webhook_secret("a" * 257))


if __name__ == "__main__":
    unittest.main()
