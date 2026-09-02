# ADR-0006: `importlib.resources` for packaged assets

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra ships package data (default rules TOML, the brand SVG) that views and infrastructure must locate at runtime. Hard-coded paths break under editable installs (`uv run`), installed wheels, and frozen binaries.

## Decision

All packaged assets are loaded via `importlib.resources`. The brand asset is centralised in `src/tidyra/presentation/brand.py`:

```python
from importlib.resources import files
from pathlib import Path

def logo_path() -> Path:
    return Path(str(files("tidyra.resources").joinpath("tidyra-logo.svg")))
```

Resources are declared under `[tool.hatch.build.targets.wheel].artifacts` so they ship with the wheel:

```toml
artifacts = ["src/tidyra/resources/*.toml", "src/tidyra/resources/*.svg"]
```

Code MUST NOT use `__file__`-relative paths to load packaged assets. The rule is enforced by code review.

## Consequences

- Positive: assets work under editable installs, installed wheels, and PyInstaller-frozen binaries.
- Positive: one helper (`logo_path()`) is the only place that knows the asset layout — easy to test, easy to swap.
- Negative: any new asset type requires updating the hatch artifact glob.
- Negative: a reader unfamiliar with `importlib.resources` may mistake the helper for a plain Path constant. The docstring explains why.
- Follow-ups: when adding audio, fonts, or other binary assets, the same pattern applies — declare in hatch, load via `files(...)`.