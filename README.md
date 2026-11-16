[![progress-banner](https://backend.codecrafters.io/progress/redis/2aa38105-f82b-4671-9a32-e57d9634968f)](https://app.codecrafters.io/users/kenshimota?r=2qF)

# Build Your Own Redis (Python)

A toy Redis clone written in Python, built as part of the
["Build Your Own Redis" Challenge](https://codecrafters.io/challenges/redis).

The goal is to progressively implement a Redis-compatible server that handles
commands like `PING`, `SET` and `GET`, while learning about event loops, the
Redis protocol (RESP) and more.

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge.

## Requirements

- [Python 3.14+](https://www.python.org/) (see `pyproject.toml` and
  `codecrafters.yml`)
- [uv](https://docs.astral.sh/uv/) for dependency management

## Project structure

```
.
├── app/
│   └── main.py          # Entry point: Redis server implementation
├── .codecrafters/       # CodeCrafters build/run scripts
├── your_program.sh      # Helper script to run the server locally
├── codecrafters.yml     # CodeCrafters configuration (Python version, debug)
└── pyproject.toml       # Project metadata and dependencies
```

## Running locally

Start the server with:

```sh
./your_program.sh
```

The server listens on `localhost:6379`, the default Redis port. You can interact
with it using `redis-cli`:

```sh
redis-cli ping
# PONG
```

## Submitting to CodeCrafters

The entry point for the implementation is `app/main.py`. Once you've made
changes, run the tests on CodeCrafters' servers with:

```sh
codecrafters submit
```

Test output will be streamed to your terminal.

## Troubleshooting

### module `socket` has no attribute `create_server`

When running your server locally, you might see an error like this:

```
Traceback (most recent call last):
  File "/.../python3.7/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "/.../python3.7/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "/app/app/main.py", line 11, in <module>
    main()
  File "/app/app/main.py", line 6, in main
    s = socket.create_server(("localhost", 6379), reuse_port=True)
AttributeError: module 'socket' has no attribute 'create_server'
```

This is because `socket.create_server` was introduced in Python 3.8, and you
might be running an older version.

You can fix this by installing Python 3.8 (or newer) locally and using that.

If you'd like to use a different version of Python, change the `buildpack` value
in `codecrafters.yml`.
