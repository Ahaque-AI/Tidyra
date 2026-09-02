"""Organization rules — configuration that maps files to destinations.

Rules are data, not code. They are loaded from TOML, merged with built-in
defaults, and consumed by strategies. Strategies must not embed rule logic
directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class OrganizationRule:
    """A single classification rule.

    A file matches a rule when its extension appears in ``extensions`` or
    when ``always_matches`` is True. The first matching rule at the
    highest ``priority`` wins. When two rules at the same priority both
    match, the file is flagged as a ``RULE_CONFLICT`` and skipped.

    Attributes:
        name: Stable identifier; used to override built-in defaults by name.
        destination: Directory relative to the scan root (e.g. ``"Images"``).
        extensions: File extensions (with leading dot, lowercase) this rule
            matches. Ignored when ``always_matches`` is True.
        patterns: Reserved for future glob-pattern support. Not used yet.
        priority: Higher wins. Built-ins default to ``10``; catch-alls to ``0``.
        always_matches: If True, the rule matches every file regardless of
            extension. Used for catch-all destinations like ``Misc/``.
    """

    name: str
    destination: str
    extensions: frozenset[str] = field(default_factory=frozenset)
    patterns: tuple[str, ...] = ()
    priority: int = 0
    always_matches: bool = False

    def matches(self, extension: str, name: str) -> bool:
        """Return True if this rule applies to a file with the given extension.

        ``name`` is accepted for API stability — pattern-based rules will
        use it once the patterns field is implemented.
        """
        if self.always_matches:
            return True
        ext = extension.lower()
        return bool(ext and ext in self.extensions)

    def with_extensions(self, extensions: frozenset[str]) -> OrganizationRule:
        """Return a copy of this rule with a different extensions set."""
        return OrganizationRule(
            name=self.name,
            destination=self.destination,
            extensions=extensions,
            patterns=self.patterns,
            priority=self.priority,
            always_matches=self.always_matches,
        )
