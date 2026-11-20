# AGENTS.md

Toy Redis clone for the CodeCrafters "Build Your Own Redis" challenge. Work is driven by staged remote tests, not by a local suite.

## Commands

- Run server: `./your_program.sh` (or `uv run --quiet -m app.main`).
  Run it as a module from the repo root; imports are absolute (`app.inputs...`), so `python app/main.py` fails.
- Manual check: `redis-cli ping` expects `PONG`. Stop the server before restarting; it binds `localhost:6379`.
- Submit / verify: `codecrafters submit`. Tests run on CodeCrafters' servers and output streams back; there is no local test command.
- `uv` manages the environment; Python is pinned to 3.14 (`.python-version`, `codecrafters.yml`). No lint, formatter, or typecheck config exists — don't invent one.

## Layout

- `app/main.py` — entrypoint: creates the listening socket and accepts connections in a loop.
- `app/inputs/read_input_redis.py` — per-connection read/reply logic; RESP parsing belongs here.
- `.codecrafters/run.sh` — what CodeCrafters executes remotely. `your_program.sh` is a local copy; editing one does not change the other.
- `.codecrafters/compile.sh` — intentionally empty (no build step for Python).

## Subagents

- `tutor` — diagnoses a failing stage and gives the smallest Socratic hint. Read-only; may only run `codecrafters test` and read-only git. Never ask it to write code.
- `refactor` — reviews duplication/design and evaluates the student's approach. Read-only; explains conceptually, no code.

## Gotchas

- The accept loop handles one client at a time; a connected client blocks others. Matters once the "multiple concurrent clients" stage is reached (consider threads or `selectors`/event loop).
- `recv(1024)` gives arbitrary chunks: a single command can be split across reads and multiple commands can arrive in one. Buffer and parse RESP incrementally rather than assuming one request per `recv`.
- Reply with `sendall` on the connected socket; `sendto` with the peer address only works incidentally.
- A stale server on port 6379 causes bind failures, and `reuse_port=True` can let two instances share the port and split traffic. Kill leftovers first.
- CodeCrafters commits use `[skip ci]`; don't mirror that convention for normal changes unless asked.
