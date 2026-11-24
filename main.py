#!/usr/bin/env python3
"""Write the out-of-office reply to /output/entry.txt.

Deterministic: no network, no clock, no randomness. The entry is a fixed
string. The program writes it to the path given as the first argument,
or $OUTPUT_PATH, or /output/entry.txt by default, and enforces the
competition gate: 1 to 140 characters, not only white space.
"""

import os
import sys
from pathlib import Path

ENTRY = (
    'I am out of office. Please direct all emergencies to my cactus. '
    'It is the only one here with boundaries.'
)

MIN_CHARS = 1
MAX_CHARS = 140
DEFAULT_PATH = "/output/entry.txt"


def gate_error(text: str) -> str | None:
    """Return why the entry fails the competition gate, or None if it passes."""
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        return f"entry is {len(text)} characters, gate is {MIN_CHARS} to {MAX_CHARS}"
    if not text.strip():
        return "entry is only white space"
    if "\n" in text:
        return "entry must be one line"
    return None


def path_from_argv(argv: list[str]) -> Path | None:
    """Return the output path from the first argument, or None if absent."""
    if len(argv) > 1:
        return Path(argv[1])
    return None


def path_from_env(env: dict[str, str]) -> Path | None:
    """Return the output path from $OUTPUT_PATH, or None if unset or blank."""
    value = env.get("OUTPUT_PATH", "").strip()
    if value:
        return Path(value)
    return None


def default_path() -> Path:
    """Return the default output path used when no other source gives one."""
    return Path(DEFAULT_PATH)


def resolve_output_path(argv: list[str] | None = None,
                       env: dict[str, str] | None = None) -> Path:
    """Pick the output path: first argument, then $OUTPUT_PATH, then default.

    Each source is checked by its own helper, in priority order, so a
    caller can see exactly which source supplied the path.
    """
    if argv is None:
        argv = sys.argv
    if env is None:
        env = os.environ
    return path_from_argv(argv) or path_from_env(env) or default_path()


def validate(text: str) -> None:
    """Enforce the competition gate, raising a clear error on failure.

    The gate (see RULES.txt) is 1 to 140 characters, not only white space,
    and a single line. A failed gate is a hard error: the entry must not
    be written, and the program must exit non-zero.
    """
    error = gate_error(text)
    if error is not None:
        raise ValueError(f"entry fails the gate: {error}")


USAGE = """usage: main.py [-h] [OUTPUT_PATH]

Write the out-of-office reply (104 characters) to OUTPUT_PATH.

positional arguments:
  OUTPUT_PATH   where to write the reply (default: $OUTPUT_PATH,
                or /output/entry.txt when unset)

options:
  -h, --help    show this help message and exit

The reply is fixed and always passes the competition gate of 1 to 140
characters, a single line, not only white space.
"""


def print_usage() -> None:
    """Print usage information to standard output."""
    print(USAGE, end="")


def write_entry(path: Path, text: str) -> None:
    """Write the entry to path, raising a clear error if it cannot be written.

    Covers both creating the parent directory and writing the file, so a
    bad output path (for example a parent that is an existing file, or a
    read-only directory) fails with a plain message instead of a traceback.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise OSError(f"cannot write entry to {path}: {exc.strerror or exc}") from exc


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print_usage()
        return 0
    try:
        validate(ENTRY)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    text = ENTRY
    path = resolve_output_path()
    try:
        write_entry(path, text)
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"wrote {len(text)} characters to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
