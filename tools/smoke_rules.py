"""Smoke-test the rule engine end-to-end.

Runs without launching the UI — exercises the configuration loader,
the strategy, the destination-rendering, and the plan validator.
"""

from __future__ import annotations

import time
from pathlib import Path

from tidyra.domain.models import FileEntry
from tidyra.domain.plans import PlanValidator
from tidyra.domain.strategies import RuleBasedStrategy
from tidyra.infrastructure.configuration import get_config_service

# 1) Load defaults
rules = list(get_config_service().load())
print(f"Loaded {len(rules)} default rules")

for r in rules:
    extras: list[str] = []
    if r.name_patterns:
        extras.append("patterns=" + repr(list(r.name_patterns)))
    if "{" in r.destination:
        extras.append("dest-templated=" + repr(r.destination))
    extras_str = "  ".join(extras)
    print(f"  - {r.name:25s} pri={r.priority:3d}  dest={r.destination!r:48s}  {extras_str}")


# 2) Build a synthetic root and verify each interesting case
root = Path("C:/Users/Abdul/synthetic-tidyra-root")
entries = [
    # Vacation photo by name → high-priority rule beats generic photo
    FileEntry(
        path=root / "IMG_vacation_2024.jpg",
        name="IMG_vacation_2024.jpg",
        extension=".jpg",
        size=12345,
        mtime=time.mktime((2024, 6, 15, 10, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Screenshot by name on Windows
    FileEntry(
        path=root / "Screenshot 2024-01-02 123456.png",
        name="Screenshot 2024-01-02 123456.png",
        extension=".png",
        size=6789,
        mtime=time.mktime((2024, 1, 2, 12, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Tax document by name, going into Finance/Tax/{year}
    FileEntry(
        path=root / "tax-return-2024.pdf",
        name="tax-return-2024.pdf",
        extension=".pdf",
        size=45678,
        mtime=time.mktime((2024, 4, 10, 9, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Plain photo, no name hint → should land in Photos/{year}
    FileEntry(
        path=root / "IMG_20240315_143022.jpg",
        name="IMG_20240315_143022.jpg",
        extension=".jpg",
        size=23456,
        mtime=time.mktime((2024, 3, 15, 14, 30, 22, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Music → Music/
    FileEntry(
        path=root / "song.mp3",
        name="song.mp3",
        extension=".mp3",
        size=89012,
        mtime=time.mktime((2023, 12, 1, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Unknown extension → catch-all Misc
    FileEntry(
        path=root / "mystery.xyz",
        name="mystery.xyz",
        extension=".xyz",
        size=10,
        mtime=time.mktime((2024, 1, 1, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
]

validator = PlanValidator(root=root, destination_exists=lambda _p: False)
strategy = RuleBasedStrategy(validator=validator)
plan = strategy.create_plan(root=root, entries=entries, rules=rules)

print("\nPlan results:")
for op in plan.operations:
    rel = op.destination.relative_to(root)
    status = "EXECUTE" if op.will_execute else f"SKIP({op.skip_reason})"
    print(f"  [{status}] {op.source.name:35s} -> {rel}   (rule={op.rule_name})")

# Expectations:
# - IMG_vacation_2024.jpg → Photos/Trips/Vacation/...
# - Screenshot *.png → Screenshots/...
# - tax-return-2024.pdf → Documents/Finance/Tax/2024/...
# - IMG_20240315... → Photos/2024/...
# - song.mp3 → Music/...
# - mystery.xyz → Misc/...
expected = {
    "IMG_vacation_2024.jpg": "Photos/Trips/Vacation",
    "Screenshot 2024-01-02 123456.png": "Screenshots",
    "tax-return-2024.pdf": "Documents/Finance/Tax/2024",
    "IMG_20240315_143022.jpg": "Photos/2024",
    "song.mp3": "Music",
    "mystery.xyz": "Misc",
}

print("\nExpectation check:")


def _parent(path: Path) -> str:
    return str(path.parent.relative_to(root)).replace("\\", "/")


ok = True
for op in plan.operations:
    want = expected.get(op.source.name)
    if want is None:
        continue
    got = _parent(op.destination) if op.will_execute else ""
    pass_ = got == want
    ok = ok and pass_
    mark = "PASS" if pass_ else "FAIL"
    print(f"  [{mark}] {op.source.name:35s} want={want!r:35s}  got={got!r}")
print("\nALL GOOD" if ok else "SOME FAILED")
