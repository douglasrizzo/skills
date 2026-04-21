# /// script
# dependencies = ["mutmut>=3.5"]
# ///
"""Portable mutmut wrapper that works around the macOS setproctitle fork crash."""

import platform
import sys

from mutmut import __main__ as mutmut_main


def _noop(title: str) -> None:
  del title


def main() -> int:
  if platform.system() == "Darwin":
    mutmut_main.setproctitle = _noop
  result = mutmut_main.cli.main(
    args=sys.argv[1:],
    prog_name="mutmut",
    standalone_mode=False,
  )
  return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
  raise SystemExit(main())
