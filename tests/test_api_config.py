"""
Author: eric vanoverbeke
Date: 2026-01-18
"""

import os
import unittest

from app.main import config_payload


class TestApiConfig(unittest.TestCase):
    def test_default_language(self) -> None:
        original = os.environ.get("APP_DEFAULT_LANG")
        try:
            if "APP_DEFAULT_LANG" in os.environ:
                del os.environ["APP_DEFAULT_LANG"]
            self.assertEqual(config_payload()["default_language"], "en")

            os.environ["APP_DEFAULT_LANG"] = "fr"
            self.assertEqual(config_payload()["default_language"], "fr")

            os.environ["APP_DEFAULT_LANG"] = "zz"
            self.assertEqual(config_payload()["default_language"], "en")
        finally:
            if original is None:
                os.environ.pop("APP_DEFAULT_LANG", None)
            else:
                os.environ["APP_DEFAULT_LANG"] = original
