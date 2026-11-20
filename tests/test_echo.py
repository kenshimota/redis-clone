"""Tests for the "respond to ECHO" stage (RESP bulk-string echo)."""

import unittest

from tests.support import RedisError, ServerHarness, encode


def encode_many(*commands: tuple[str, str]) -> bytes:
    """Concatenate several commands into one RESP byte string."""
    return b"".join(encode(*command) for command in commands)


class EchoTest(unittest.TestCase):
    def test_echo_returns_the_argument_as_bulk_string(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("ECHO", "hola")
                self.assertEqual(conn.read(), b"hola")

    def test_echo_empty_string_returns_empty_bulk_string(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("ECHO", "")
                self.assertEqual(conn.read(), b"")

    def test_echo_preserves_spaces_inside_the_value(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("ECHO", "hello world")
                self.assertEqual(conn.read(), b"hello world")

    def test_echo_command_name_is_case_insensitive(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                for spelling in ("echo", "EcHo"):
                    with self.subTest(spelling=spelling):
                        conn.send(spelling, "valor")
                        self.assertEqual(conn.read(), b"valor")

    def test_echo_with_extra_arguments_returns_an_error(self) -> None:
        # Real Redis rejects wrong arity: "ERR wrong number of arguments
        # for 'echo' command". CodeCrafters only sends one argument, but a
        # second one must not be silently ignored or concatenated.
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("ECHO", "uno", "dos")
                with self.assertRaises(RedisError):
                    conn.read()

    def test_echo_without_argument_returns_an_error(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("ECHO")
                with self.assertRaises(RedisError):
                    conn.read()

    def test_ping_and_echo_share_a_connection_without_losing_replies(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send("PING")
                self.assertEqual(conn.read(), "PONG")
                conn.send("ECHO", "hola")
                self.assertEqual(conn.read(), b"hola")
                conn.send("ECHO", "adios")
                self.assertEqual(conn.read(), b"adios")
                conn.send("PING")
                self.assertEqual(conn.read(), "PONG")

    def test_two_echo_commands_in_one_packet(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                conn.send_raw(
                    encode_many(("ECHO", "uno"), ("ECHO", "dos"))
                )
                self.assertEqual(conn.read(), b"uno")
                self.assertEqual(conn.read(), b"dos")

    def test_echo_split_across_two_sends(self) -> None:
        with ServerHarness() as server:
            with server.connect() as conn:
                value = b"partido"
                command = encode("ECHO", value.decode())
                # Split inside the bulk payload, so no reply can be built
                # until the rest of the command arrives.
                cut = command.index(value) + 3
                conn.send_raw(command[:cut])
                conn.send_raw(command[cut:])
                self.assertEqual(conn.read(), value)


if __name__ == "__main__":
    unittest.main()
