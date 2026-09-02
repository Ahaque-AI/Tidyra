"""Tidyra logging — structured logging with :mod:`loguru`.

This module is the single owner of loguru configuration. Call
:func:`configure_logging` once at process start (the Flet entry point
already does this); every other module imports :data:`logger` directly
from loguru and uses :meth:`loguru.Logger.bind` for structured context.

Why a single module instead of letting callers configure loguru directly:

* Centralises the format and sink list so the on-disk shape is consistent
  across Flet entry, ``python -m tidyra``, and any future CLI.
* Keeps the rest of the codebase free of ``sys.stderr`` plumbing and
  ``format=...`` strings.
* Makes it trivial to add a rotating JSON sink, swap the console sink
  for a TTY check, or send records to a remote collector — change here
  once, change everywhere.

Configuration is controlled by environment variables so the file sink and
level can be tuned without editing code:

* ``TIDYRA_LOG_LEVEL`` — root level for the console sink. Default
  ``"INFO"``. Accepts the standard ``loguru``/``logging`` level names.
* ``TIDYRA_LOG_FILE`` — absolute path for the JSON file sink. When set,
  records are mirrored there with ``serialize=True``. When unset (the
  default), the file sink is disabled and only the console sink is
  installed.

Structured logging convention:

* Use :meth:`logger.bind` to attach key/value context (``file_path``,
  ``rule_name``, ``skip_reason``, etc.) so every record carries those
  fields.
* Use :meth:`logger.exception` inside ``except`` blocks — loguru
  captures the traceback automatically and the ``exception`` record
  field is set on the JSON record.
* Treat the module-level :data:`logger` as the only logging API elsewhere
  in the codebase. Importing :mod:`loguru` directly outside this module
  is a code-review smell.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from loguru import logger

# Default log level when TIDYRA_LOG_LEVEL is not set.
_DEFAULT_LEVEL = "INFO"

# Human-readable console format. ``{name}`` and ``{function}:{line}`` make
# it obvious which module produced each record; the bound-context fields
# appear at the end as ``key=value`` pairs.
_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def configure_logging(
    *,
    level: str | None = None,
    log_file: Path | str | None = None,
) -> None:
    """Install the Tidyra logging sinks.

    Safe to call more than once; later calls replace the previous sinks.

    Args:
        level: Console log level. Defaults to ``$TIDYRA_LOG_LEVEL`` or
            :data:`_DEFAULT_LEVEL` when unset.
        log_file: Absolute path for the JSON file sink. Defaults to
            ``$TIDYRA_LOG_FILE``; when neither is set, no file sink is
            installed and Tidyra logs only to ``stderr``.
    """
    resolved_level = (level or os.environ.get("TIDYRA_LOG_LEVEL") or _DEFAULT_LEVEL).upper()
    resolved_file = log_file or os.environ.get("TIDYRA_LOG_FILE")

    # Remove every previous sink so reconfiguration starts from a clean
    # slate. Loguru's ``remove()`` with no args drops them all.
    logger.remove()

    # Console sink — coloured, human-friendly, on by default.
    logger.add(
        sys.stderr,
        level=resolved_level,
        format=_CONSOLE_FORMAT,
        backtrace=False,
        diagnose=False,
        enqueue=False,
    )

    # File sink — JSON, machine-friendly. When enabled, every record is
    # also written here so downstream tools (log shippers, dashboards,
    # bug reports) can ingest the same records the developer sees.
    if resolved_file:
        log_path = Path(resolved_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            level=resolved_level,
            serialize=True,
            enqueue=False,
            rotation="10 MB",
            retention=5,
            compression=None,
        )

    logger.bind(
        component="logging",
        level=resolved_level,
        file=str(resolved_file) if resolved_file else None,
    ).info("tidyra logging configured")


__all__ = ["configure_logging", "logger"]
