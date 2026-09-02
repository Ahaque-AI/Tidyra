"""Organization rules — configuration that maps files to destinations.

Rules are data, not code. They are loaded from TOML, merged with built-in
defaults, and consumed by strategies. Strategies must not embed rule logic
directly.

A rule matches a file when **any** of its matchers hits:

- one of the file's extensions appears in ``extensions``
- the file's name matches one of the glob ``name_patterns``
  (case-insensitive ``fnmatch``)

The first rule at the highest ``priority`` wins. Ties at the same priority
are flagged as ``RULE_CONFLICT`` and skipped.

``destination`` may contain template variables that resolve from the file
itself (``{year}``, ``{month}``, ``{ext}``, ``{stem}``). The substitution
helper lives in :func:`render_destination`.

``always_matches`` is retained for backward compatibility with v0.1.0
configs. New rules should prefer ``name_patterns = ['*']``.
"""

from __future__ import annotations

import datetime as _dt
import fnmatch
from dataclasses import dataclass, field

from tidyra.domain.models import FileEntry


@dataclass(frozen=True, slots=True)
class OrganizationRule:
    """A single classification rule.

    Attributes:
        name: Stable identifier; used to override built-in defaults by name.
        destination: Directory relative to the scan root. Supports templates
            such as ``Photos/By-Year/{year}`` — see :func:`render_destination`.
        extensions: File extensions (with leading dot, lowercase) this rule
            matches. Empty when the rule matches by name only.
        name_patterns: Glob patterns (case-insensitive) the file name must
            match. ``["Screenshot*"]`` matches ``Screenshot 2024-01-01.png``.
            ``["*"]`` is the explicit catch-all.
        priority: Higher wins. Built-ins default to ``10``; catch-alls to ``0``.
        always_matches: Deprecated. Kept so older configs still parse —
            equivalent to ``name_patterns = ['*']`` for matching purposes.
    """

    name: str
    destination: str
    extensions: frozenset[str] = field(default_factory=frozenset)
    name_patterns: tuple[str, ...] = ()
    priority: int = 0
    always_matches: bool = False

    def matches(self, extension: str, name: str) -> bool:
        """Return True if this rule applies to a file with the given extension/name.

        Matching policy:

        - ``always_matches`` short-circuits to True (legacy form).
        - If both ``extensions`` and ``name_patterns`` are set, the file must
          satisfy **both** — extension is one of the listed extensions AND
          name matches one of the globs. This is the "name AND format
          together" semantic the user asked for.
        - If only one of ``extensions`` or ``name_patterns`` is set, that
          single condition decides.
        - If neither is set, the rule does not match.
        """
        if self.always_matches:
            return True
        ext_match: bool
        ext = extension.lower()
        ext_match = bool(ext) and ext in self.extensions

        name_match: bool
        if self.name_patterns:
            lowered = name.lower()
            name_match = any(
                fnmatch.fnmatchcase(lowered, pattern.lower())
                for pattern in self.name_patterns
            )
        else:
            name_match = False

        if self.extensions and self.name_patterns:
            return ext_match and name_match
        if self.extensions:
            return ext_match
        if self.name_patterns:
            return name_match
        return False

    def with_extensions(self, extensions: frozenset[str]) -> OrganizationRule:
        """Return a copy of this rule with a different extensions set."""
        return OrganizationRule(
            name=self.name,
            destination=self.destination,
            extensions=extensions,
            name_patterns=self.name_patterns,
            priority=self.priority,
            always_matches=self.always_matches,
        )


def render_destination(template: str, entry: FileEntry) -> str:
    """Expand ``{year}``, ``{month}``, ``{ext}``, ``{stem}`` in a destination.

    Unknown placeholders are left as literal text so the user sees what
    they got wrong instead of a silent substitution to empty string.

    The timestamp is read from ``entry.mtime`` (the file's last-modified
    time). We never read file contents — see the design discussion in
    ``docs/plans/2026-09-02--rule-engine-v2.md`` and ADR-0008.
    """
    if "{" not in template:
        return template
    moment = _dt.datetime.fromtimestamp(entry.mtime)
    mapping = {
        "year": f"{moment.year:04d}",
        "month": f"{moment.month:02d}",
        "ext": entry.extension.lstrip(".").lower() or "file",
        "stem": entry.stem,
    }
    out: list[str] = []
    i = 0
    while i < len(template):
        ch = template[i]
        if ch != "{":
            out.append(ch)
            i += 1
            continue
        end = template.find("}", i)
        if end == -1:
            out.append(template[i:])
            break
        key = template[i + 1 : end]
        out.append(mapping.get(key, "{" + key + "}"))
        i = end + 1
    return "".join(out)


__all__ = ["OrganizationRule", "render_destination"]
