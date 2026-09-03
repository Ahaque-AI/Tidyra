"""Organization rules — configuration that maps files to destinations.

Rules are data, not code. They are loaded from TOML, merged with built-in
defaults, and consumed by strategies. Strategies must not embed rule logic
directly.

A rule matches a file when its configured matcher groups hit:

- one of the file's extensions appears in ``extensions``
- the file's name matches one of the glob ``name_patterns``
  (case-insensitive ``fnmatch``)
- the file's name matches one of the ``name_regexes``
  (case-insensitive regular-expression search)
- an optional ``topic_regex`` matches and captures a named ``topic`` group

The first rule at the highest ``priority`` wins. Ties at the same priority
are flagged as ``RULE_CONFLICT`` and skipped.

``destination`` may contain template variables that resolve from the file
itself (``{date}``, ``{year}``, ``{month}``, ``{ext}``, ``{stem}``, ``{topic}``). The
substitution helper lives in :func:`render_destination`.

``always_matches`` is retained for backward compatibility with v0.1.0
configs. New rules should prefer ``name_patterns = ['*']``.
"""

from __future__ import annotations

import datetime as _dt
import fnmatch
import re
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
        name_regexes: Regular expressions (case-insensitive) searched in the
            file name. They are an alternative to ``name_patterns``.
        topic_regex: Optional regular expression with a named ``topic`` group.
            The captured value can be used with ``{topic}`` in a destination.
        priority: Higher wins. Built-ins default to ``10``; catch-alls to ``0``.
        always_matches: Deprecated. Kept so older configs still parse —
            equivalent to ``name_patterns = ['*']`` for matching purposes.
    """

    name: str
    destination: str
    extensions: frozenset[str] = field(default_factory=frozenset)
    name_patterns: tuple[str, ...] = ()
    name_regexes: tuple[str, ...] = ()
    topic_regex: str | None = None
    priority: int = 0
    always_matches: bool = False

    def matches(self, extension: str, name: str) -> bool:
        """Return True if this rule applies to a file with the given extension/name.

        Matching policy:

        - ``always_matches`` short-circuits to True (legacy form).
        - Glob patterns and regular expressions are alternative name matchers.
        - If both ``extensions`` and a name matcher are set, the file must
          satisfy **both** — extension is one of the listed extensions AND
          name matches a glob or regular expression.
        - If only one matcher kind is set, that
          single condition decides.
        - If neither is set, the rule does not match.
        """
        if self.always_matches:
            return True
        ext_match: bool
        ext = extension.lower()
        ext_match = bool(ext) and ext in self.extensions

        lowered = name.lower()
        name_match = any(
            fnmatch.fnmatchcase(lowered, pattern.lower()) for pattern in self.name_patterns
        ) or any(re.search(pattern, name, flags=re.IGNORECASE) is not None for pattern in self.name_regexes)
        topic_match = self.topic_regex is not None and re.search(
            self.topic_regex, name, flags=re.IGNORECASE
        ) is not None
        has_name_matcher = bool(self.name_patterns or self.name_regexes or self.topic_regex)
        name_match = name_match or topic_match

        if self.extensions and has_name_matcher:
            return ext_match and name_match
        if self.extensions:
            return ext_match
        if has_name_matcher:
            return name_match
        return False

    def with_extensions(self, extensions: frozenset[str]) -> OrganizationRule:
        """Return a copy of this rule with a different extensions set."""
        return OrganizationRule(
            name=self.name,
            destination=self.destination,
            extensions=extensions,
            name_patterns=self.name_patterns,
            name_regexes=self.name_regexes,
            topic_regex=self.topic_regex,
            priority=self.priority,
            always_matches=self.always_matches,
        )

    def topic_for(self, name: str) -> str | None:
        """Return a safe named topic captured by ``topic_regex``."""
        if self.topic_regex is None:
            return None
        match = re.search(self.topic_regex, name, flags=re.IGNORECASE)
        if match is None:
            return None
        topic = match.groupdict().get("topic")
        if not topic:
            return None
        cleaned = re.sub(r"[^A-Za-z0-9 _.-]+", "_", topic).strip(" .")
        if not cleaned or cleaned.upper() in {"CON", "PRN", "AUX", "NUL"}:
            return None
        return cleaned


def render_destination(
    template: str, entry: FileEntry, *, topic: str | None = None
) -> str:
    """Expand ``{date}``, ``{year}``, ``{month}``, ``{ext}``, ``{stem}``.

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
        "date": f"{moment.year:04d}-{moment.month:02d}-{moment.day:02d} — {moment.day} {moment.strftime('%B')} {moment.year:04d}",
        "year": f"{moment.year:04d}",
        "month": f"{moment.month:02d}",
        "ext": entry.extension.lstrip(".").lower() or "file",
        "stem": entry.stem,
        "topic": topic or "{topic}",
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
