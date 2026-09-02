"""Smoke-test the cross-platform packaging setup.

Validates the things the CI pipeline needs without actually running
``flet build`` (which downloads ~500 MB of Flutter SDK and takes
minutes). If this script passes, the release workflow has the inputs
it expects.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

import yaml  # type: ignore[import-untyped]  # types-PyYAML not in dev deps

ROOT = Path(__file__).resolve().parent.parent


def ok(label: str) -> None:
    print(f"  [PASS] {label}")


def fail(label: str) -> None:
    print(f"  [FAIL] {label}")
    raise SystemExit(1)


def main() -> None:
    # 1. Workflow files parse as valid YAML
    for name in ("release.yml", "ci.yml"):
        path = ROOT / ".github" / "workflows" / name
        if not path.exists():
            fail(f"missing workflow: {path}")
        try:
            parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            fail(f"invalid YAML in {path}: {exc}")
        ok(f"{path.relative_to(ROOT)} parses; jobs={list(parsed['jobs'].keys())}")

    # 2. pyproject.toml loads and the entry point + artifacts match expectations
    with (ROOT / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    if data["project"]["scripts"].get("tidyra") != "tidyra.presentation.app:run":
        fail("pyproject 'tidyra' script entry point changed unexpectedly")
    ok("pyproject.toml tidyra entry point = tidyra.presentation.app:run")
    artifacts = data["tool"]["hatch"]["build"]["targets"]["wheel"]["artifacts"]
    for ext in (".toml", ".svg", ".ico"):
        if not any(ext in glob for glob in artifacts):
            fail(f"hatch artifacts missing {ext}")
    ok(f"pyproject artifacts glob: {artifacts}")

    # 2b. [tool.flet.app] resolves to a real .py file (entry-point shim)
    flet_cfg = data["tool"]["flet"]["app"]
    pkg_path = ROOT / flet_cfg["path"]
    entry = pkg_path / (Path(flet_cfg["module"]).stem + ".py")
    if not entry.exists():
        fail(f"[tool.flet.app] entry file missing: {entry}")
    ok(f"[tool.flet.app] entry = {entry.relative_to(ROOT)} (path={flet_cfg['path']}, module={flet_cfg['module']})")
    if not (pkg_path / "__init__.py").exists():
        fail(f"[tool.flet.app] path {pkg_path} is not a package (no __init__.py)")
    ok(f"[tool.flet.app] path {pkg_path.relative_to(ROOT)} is the tidyra package")

    # 3. Icon set is present
    icons = ROOT / "assets" / "icons"
    required_files = [
        "tidyra-icon.ico",
        "icon.png",
    ]
    for rel in required_files:
        if not (icons / rel).exists():
            fail(f"missing icon: {icons / rel}")
    ok(f"required icon files present: {required_files}")

    # 4. Multi-size PNG set is complete
    sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
    for size in sizes:
        png = icons / "png" / f"tidyra-icon-{size}.png"
        if not png.exists():
            fail(f"missing PNG size: {png}")
        if png.stat().st_size < 50:
            fail(f"PNG too small ({png.stat().st_size} bytes): {png}")
    ok(f"all {len(sizes)} PNG sizes present and non-trivial")

    # 5. Runtime icon is reachable via importlib.resources
    from importlib.resources import files
    runtime_ico = Path(str(files("tidyra.resources").joinpath("tidyra-icon.ico")))
    if not runtime_ico.exists():
        fail(f"runtime icon not resolvable: {runtime_ico}")
    ok(f"runtime icon resolves to: {runtime_ico.relative_to(ROOT)} ({runtime_ico.stat().st_size} bytes)")

    # 6. .gitignore has dist/
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "dist/" not in gi:
        fail(".gitignore missing dist/ entry")
    ok(".gitignore excludes dist/")

    # 7. dist/ does not already exist (would mean the user has stale local builds)
    dist = ROOT / "dist"
    if dist.exists():
        print(f"  [WARN] dist/ exists at {dist} — content: {list(dist.iterdir())}")
    else:
        ok("no stale dist/ directory")

    # 8. Prefetch script for the Flet template cache is present
    prefetch = ROOT / "tools" / "prefetch_flet_template.py"
    if not prefetch.exists():
        fail(f"missing {prefetch}")
    ok(f"prefetch helper: {prefetch.relative_to(ROOT)}")

    print("\nALL GOOD")


if __name__ == "__main__":
    main()
