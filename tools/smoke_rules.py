"""Smoke-test the rule engine end-to-end.

Runs without launching the UI — exercises the configuration loader,
the strategy, the destination-rendering, and the plan validator.
"""

from __future__ import annotations

import tempfile
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
root = Path(tempfile.mkdtemp(prefix="tidyra-smoke-")).resolve()
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
    # Unknown extension → explicit review queue
    FileEntry(
        path=root / "mystery.xyz",
        name="mystery.xyz",
        extension=".xyz",
        size=10,
        mtime=time.mktime((2024, 1, 1, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Known project document → named project, not generic Documents
    FileEntry(
        path=root / "ArangoDB architecture.pdf",
        name="ArangoDB architecture.pdf",
        extension=".pdf",
        size=23456,
        mtime=time.mktime((2024, 5, 9, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Code → useful language folder, not generic Code
    FileEntry(
        path=root / "organize.py",
        name="organize.py",
        extension=".py",
        size=1234,
        mtime=time.mktime((2024, 5, 10, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Recognizable coursework → education topic
    FileEntry(
        path=root / "Sajil_Agentic_Coding_Platforms_Assignment.pdf",
        name="Sajil_Agentic_Coding_Platforms_Assignment.pdf",
        extension=".pdf",
        size=34567,
        mtime=time.mktime((2024, 5, 11, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Opaque document name → review, because no honest topic can be inferred
    FileEntry(
        path=root / "SA-006.pdf",
        name="SA-006.pdf",
        extension=".pdf",
        size=45678,
        mtime=time.mktime((2024, 5, 12, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Course summary → coursework beats the lower-priority summary rule
    FileEntry(
        path=root / "Course website_summary.txt",
        name="Course website_summary.txt",
        extension=".txt",
        size=5678,
        mtime=time.mktime((2024, 5, 13, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
    # Resume → career folder
    FileEntry(
        path=root / "Abdul Haque Agentic AI Engineer Resume.pdf",
        name="Abdul Haque Agentic AI Engineer Resume.pdf",
        extension=".pdf",
        size=67890,
        mtime=time.mktime((2024, 5, 14, 0, 0, 0, 0, 0, 0)),
        is_symlink=False,
        is_directory=False,
    ),
]

validator = PlanValidator(root=root, destination_exists=lambda _p: False)
strategy = RuleBasedStrategy(validator=validator)
plan = strategy.create_plan(root=root, entries=entries, rules=rules)

print("\nPlan results:")
for op in plan.operations:
    rel = op.destination.resolve().relative_to(root)
    status = "EXECUTE" if op.will_execute else f"SKIP({op.skip_reason})"
    print(f"  [{status}] {op.source.name:35s} -> {rel}   (rule={op.rule_name})")

# Expectations use the current date-first destination contract.
expected = {
    "IMG_vacation_2024.jpg": "2024-06-15 — 15 June 2024/Photos/Trips/Vacation",
    "Screenshot 2024-01-02 123456.png": "2024-01-02 — 2 January 2024/Images/Screenshots",
    "tax-return-2024.pdf": "2024-04-10 — 10 April 2024/Documents/Finance/Tax",
    "IMG_20240315_143022.jpg": "2024-03-15 — 15 March 2024/Images",
    "song.mp3": "2023-12-01 — 1 December 2023/Music",
    "mystery.xyz": "2024-01-01 — 1 January 2024/Needs Review/xyz",
    "ArangoDB architecture.pdf": "2024-05-09 — 9 May 2024/Documents/Projects/ArangoDB",
    "organize.py": "2024-05-10 — 10 May 2024/Code/Python",
    "Sajil_Agentic_Coding_Platforms_Assignment.pdf": "2024-05-11 — 11 May 2024/Documents/Education/Agentic Coding Platforms",
    "SA-006.pdf": "2024-05-12 — 12 May 2024/Needs Review/Documents",
    "Course website_summary.txt": "2024-05-13 — 13 May 2024/Documents/Education/Coursework",
    "Abdul Haque Agentic AI Engineer Resume.pdf": "2024-05-14 — 14 May 2024/Documents/Career/Resumes",
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
if not ok:
    raise SystemExit("SOME FAILED")
print("\nALL GOOD")
