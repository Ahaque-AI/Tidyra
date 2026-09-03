"""Smoke-test the flet build entry-point resolution.

Replicates the logic in ``flet_cli/commands/build_base.py`` to confirm
``tool.flet.app`` in pyproject.toml resolves to a real .py file and
that the resulting ``package_app_path`` covers the whole ``tidyra``
package — so serious_python can package it and the runtime can
resolve ``import tidyra`` and friends.
"""

from __future__ import annotations

import importlib.util
import inspect
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

with (ROOT / "pyproject.toml").open("rb") as f:
    data = tomllib.load(f)

flet_cfg = data["tool"]["flet"]["app"]
pkg_path = ROOT / flet_cfg["path"]
module = flet_cfg["module"]
mod_filename = Path(module).stem + ".py"
entry = pkg_path / mod_filename

print(f"tool.flet.app: {flet_cfg}")
print(f"package_app_path: {pkg_path.relative_to(ROOT)}")
print(f"entry module: {entry.relative_to(ROOT)}  exists? {entry.exists()}")
print()

# The runtime import path: package_app_path is on sys.path. The
# `tidyra` package lives at package_app_path itself.
print("runtime path layout:")
print(f"  sys.path  = {pkg_path}")
print(f"  tidyra    = {pkg_path}  ({pkg_path / '__init__.py'})")
print(f"  tidyra.main       -> {pkg_path / 'main.py'}")
print(f"  tidyra.presentation.app -> {pkg_path / 'presentation' / 'app.py'}")
print(f"  tidyra.domain     -> {pkg_path / 'domain'}")

assert (pkg_path / "__init__.py").exists(), "package_app_path is not a package"
assert entry.exists(), f"entry file {entry} missing"

# Confirm imports work via the shim.
spec = importlib.util.spec_from_file_location("tidyra_main_smoke", entry)
assert spec is not None and spec.loader is not None, "could not build spec for tidyra.main"
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, "main"), "tidyra.main did not re-export `main`"

sig = inspect.signature(mod.main)
assert list(sig.parameters.keys()) == ["page"], f"main() signature unexpected: {sig}"

print()
print("tidyra.main.main re-exports the real Flet entry correctly.")
print("ALL GOOD")
