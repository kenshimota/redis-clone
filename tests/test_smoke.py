"""Smoke test for the test harness itself (stage: respond to PING)."""

import unittest

from tests.support import ServerHarness


class PingTest(unittest.TestCase):
    def test_ping_replies_pong(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("PING")
                self.assertEqual(conn.read(), "PONG")


if __name__ == "__main__":
    unittest.main()
