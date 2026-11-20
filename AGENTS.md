# AGENTS.md

Toy Redis clone for the CodeCrafters "Build Your Own Redis" challenge. Work is driven by staged remote tests; `tests/` holds optional local tests written by the `tester` subagent.

## Commands

- Run server: `./your_program.sh` (or `uv run --quiet -m app.main`).
  Run it as a module from the repo root; imports are absolute (`app.inputs...`), so `python app/main.py` fails.
- Manual check: `redis-cli ping` expects `PONG`. Stop the server before restarting; it binds `localhost:6379`.
- Local tests (optional, stdlib `unittest`, no extra dependencies): `uv run python -m unittest discover -s tests -t . -v`.
  `tests/support.py` starts the real handler on a free port, so local tests never touch `6379`.
- Submit / verify: `codecrafters submit`. Remote tests run on CodeCrafters' servers and output streams back.
- `uv` manages the environment; Python is pinned to 3.14 (`.python-version`, `codecrafters.yml`). No lint, formatter, or typecheck config exists — don't invent one.

## Layout

- `app/main.py` — entrypoint: starts the `asyncio` server on `0.0.0.0:6379`.
- `app/connection.py` — per-connection read/reply logic; RESP parsing belongs here.
- `app/extract_commands.py` — work in progress for splitting buffered input into commands.
- `tests/` — local tests plus `support.py` (RESP client and server harness).
- `.codecrafters/run.sh` — what CodeCrafters executes remotely. `your_program.sh` is a local copy; editing one does not change the other.
- `.codecrafters/compile.sh` — intentionally empty (no build step for Python).

## Subagents

- `tutor` — diagnoses a failing stage and gives the smallest Socratic hint. Read-only; may only run `codecrafters test` and read-only git. Never ask it to write code.
- `refactor` — reviews duplication/design and evaluates the student's approach. Read-only; explains conceptually, no code.
- `tester` — asks which stage/topic the student is on, then writes failing tests in `tests/` so the student can implement against them. May only edit `tests/` and run `unittest`; never modifies `app/`.

## Gotchas

- The accept loop handles one client at a time; a connected client blocks others. Matters once the "multiple concurrent clients" stage is reached (consider threads or `selectors`/event loop).
- `recv(1024)` gives arbitrary chunks: a single command can be split across reads and multiple commands can arrive in one. Buffer and parse RESP incrementally rather than assuming one request per `recv`.
- Reply with `sendall` on the connected socket; `sendto` with the peer address only works incidentally.
- A stale server on port 6379 causes bind failures, and `reuse_port=True` can let two instances share the port and split traffic. Kill leftovers first.
- CodeCrafters commits use `[skip ci]`; don't mirror that convention for normal changes unless asked.
