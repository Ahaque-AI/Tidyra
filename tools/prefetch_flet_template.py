"""Pre-populate the Flet build-template cache.

Why this exists
---------------

``flet build`` downloads ``flet-build-template.zip`` from
``https://github.com/flet-dev/flet/releases/download/v<version>/...``
into ``$FLET_CACHE_DIR/build-template/v<version>/`` before the build
runs. On machines where DNS resolution for ``github.com`` is flaky,
unreliable, or outright blocked (corporate proxy, intermittent VPN,
captive portal), that download fails with
``socket.gaierror: [Errno 11001] getaddrinfo failed`` and the build
aborts.

The cache is "use if present, else download once" (see
``flet_cli/utils/template_cache.py``). Pre-populating it with the same
zip avoids the live download entirely. This script does exactly that,
using ``urllib.request`` — the same stdlib call flet would have made —
so behaviour is identical.

Usage::

    uv run python tools/prefetch_flet_template.py

If the cache file already exists and is non-empty, the script exits
with a friendly "already cached" message. Set ``FLET_FORCE_PREFETCH=1``
to re-download.

The cache root is ``$FLET_CACHE_DIR`` or ``~/.flet/cache``.
"""

from __future__ import annotations

import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

TEMPLATE_URL = (
    "https://github.com/flet-dev/flet/releases/download/"
    "v{version}/flet-build-template.zip"
)


def cache_root() -> Path:
    """Same logic as ``flet_cli.utils.template_cache.get_cache_root``."""
    env = os.environ.get("FLET_CACHE_DIR")
    return Path(env).expanduser() if env else Path.home() / ".flet" / "cache"


def flet_version() -> str:
    """Resolve the Flet version (matches flet-cli's default template_ref)."""
    try:
        import flet.version as v
        return v.flet_version
    except Exception:
        # Fallback: read the version constant out of the flet-cli's installed copy.
        from importlib.metadata import version as _v
        return _v("flet")


def cache_path_for(version: str, root: Path) -> Path:
    return root / "build-template" / f"v{version}" / "flet-build-template.zip"


def main() -> int:
    version = flet_version()
    url = TEMPLATE_URL.format(version=version)
    root = cache_root()
    target = cache_path_for(version, root)

    force = os.environ.get("FLET_FORCE_PREFETCH") == "1"
    if target.exists() and target.stat().st_size > 0 and not force:
        print(f"[skip] {target} ({target.stat().st_size} bytes) already cached")
        print("[info] FLET_FORCE_PREFETCH=1 to re-download")
        return 0

    print(f"[fetch] {url}")
    print(f"[dest]  {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    try:
        with urllib.request.urlopen(url, timeout=60) as resp, open(tmp, "wb") as out:
            shutil.copyfileobj(resp, out)
            out.flush()
            os.fsync(out.fileno())
    except (urllib.error.URLError, OSError) as exc:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        print(f"[fail] {exc}", file=sys.stderr)
        return 1
    os.replace(tmp, target)
    print(f"[ok]    {target.stat().st_size} bytes written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
