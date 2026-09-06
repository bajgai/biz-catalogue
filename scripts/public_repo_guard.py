#!/usr/bin/env python3
"""Compatibility wrapper around the shared guardrails CLI.

Prefer `guardrails check` / `guardrails hook` directly. This script preserves the
previous biz-catalogue entry points during migration without weakening checks.
"""

from __future__ import annotations

import subprocess
import sys


def _translate(argv: list[str]) -> list[str]:
    if not argv or argv == ["--staged"]:
        return ["check", "--staged"]
    if argv and argv[0] == "--pre-push":
        if len(argv) != 1:
            raise SystemExit("compatibility wrapper accepts only --pre-push")
        return ["hook", "pre-push"]
    if argv and argv[0] == "--history":
        return ["check", "--history", *argv[1:]]
    raise SystemExit(
        "usage: public_repo_guard.py [--staged | --history [REF ...] | --pre-push]"
    )


def _guardrails_available() -> bool:
    # -P keeps a force-added checkout module from shadowing the install.
    probe = subprocess.run(
        [sys.executable, "-P", "-c", "import guardrails"],
        capture_output=True,
        check=False,
    )
    return probe.returncode == 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        translated = _translate(args)
    except SystemExit as error:
        if isinstance(error.code, str):
            print(error.code, file=sys.stderr)
            return 2
        return int(error.code or 2)
    if not _guardrails_available():
        print(
            "BLOCKED: guardrails is not installed; install bajgai/guardrails "
            "through the declarative package policy.",
            file=sys.stderr,
        )
        return 2
    command = [sys.executable, "-P", "-m", "guardrails", *translated]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
