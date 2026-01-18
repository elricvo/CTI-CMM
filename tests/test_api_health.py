import unittest

from app.main import healthz


class TestApiHealth(unittest.TestCase):
    def test_healthz_payload(self) -> None:
        self.assertEqual(healthz(), {"status": "ok"})
