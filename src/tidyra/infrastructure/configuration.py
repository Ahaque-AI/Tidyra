"""Configuration loader — reads TOML rule files with precedence.

Discovery order (first wins; later layers are ignored):

1. User config dir (via ``platformdirs``) — ``rules.toml``
2. CWD — ``rules.toml``
3. Built-in defaults shipped as package data

Domain code never sees TOML types — only ``OrganizationRule`` dataclasses.
"""

from __future__ import annotations

import re
import tomllib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

import platformdirs
from loguru import logger

from tidyra.domain.rules import OrganizationRule


@dataclass(frozen=True, slots=True)
class RuleSource:
    """Where the active rule list came from."""

    path: Path
    origin: str  # "user" | "cwd" | "builtin"


class ConfigService:
    """Load and expose ``OrganizationRule`` lists."""

    USER_CONFIG_DIR: Path = platformdirs.user_config_path("tidyra")
    USER_CONFIG_FILE: Path = USER_CONFIG_DIR / "rules.toml"
    CWD_CONFIG_FILE: Path = Path.cwd() / "rules.toml"
    BUILTIN_NAME: str = "default_rules.toml"

    def load(self) -> Sequence[OrganizationRule]:
        """Return the active rule list."""
        rules, _ = self.load_with_source()
        return rules

    def load_with_source(self) -> tuple[Sequence[OrganizationRule], RuleSource]:
        """Try each source in order; first that exists wins."""
        for path, origin in (
            (self.USER_CONFIG_FILE, "user"),
            (self.CWD_CONFIG_FILE, "cwd"),
        ):
            if path.is_file():
                rules = self._parse_toml(path.read_bytes())
                logger.bind(
                    origin=origin,
                    path=str(path),
                    rule_count=len(rules),
                    component="config",
                ).info("loaded rule set from TOML")
                return rules, RuleSource(path=path, origin=origin)
        # Fall back to built-in defaults (always present).
        builtin = files("tidyra.resources").joinpath(self.BUILTIN_NAME)
        rules = self._parse_toml(builtin.read_bytes())
        logger.bind(
            origin="builtin",
            path=str(builtin),
            rule_count=len(rules),
            component="config",
        ).info("loaded built-in rule set")
        return rules, RuleSource(path=Path(str(builtin)), origin="builtin")

    def default_config_path(self) -> Path:
        """Path where the user can drop their own ``rules.toml``."""
        return self.USER_CONFIG_FILE

    def write_default_to_user_dir(self) -> Path:
        """Write the built-in defaults to the user config dir and return the path.

        Useful for a "save current rules" affordance. Returns the path even
        if the file already existed (no overwrite).
        """
        target = self.USER_CONFIG_FILE
        if target.exists():
            return target
        target.parent.mkdir(parents=True, exist_ok=True)
        builtin = files("tidyra.resources").joinpath(self.BUILTIN_NAME)
        target.write_bytes(builtin.read_bytes())
        return target

    @staticmethod
    def _parse_toml(data: bytes) -> Sequence[OrganizationRule]:
        payload = tomllib.loads(data.decode("utf-8"))
        rules_raw = payload.get("rule", [])
        if not isinstance(rules_raw, list):
            raise ValueError("rules.toml: top-level 'rule' must be a list of tables")
        rules: list[OrganizationRule] = []
        for entry in rules_raw:
            rules.append(ConfigService._rule_from_dict(entry))
        return tuple(rules)

    @staticmethod
    def _rule_from_dict(entry: object) -> OrganizationRule:
        if not isinstance(entry, dict):
            raise ValueError(f"rule entry must be a table: {entry!r}")
        name = entry.get("name")
        if not isinstance(name, str):
            raise ValueError(f"rule entry missing string 'name': {entry!r}")
        destination = entry.get("destination")
        if not isinstance(destination, str):
            raise ValueError(f"rule {name!r} missing string 'destination'")
        ext_list = entry.get("extensions", [])
        if not isinstance(ext_list, list):
            raise ValueError(f"rule {name!r} 'extensions' must be a list")
        extensions = frozenset(str(e).lower() for e in ext_list if isinstance(e, str))
        name_patterns_raw = entry.get("name_patterns", entry.get("patterns", []))
        if not isinstance(name_patterns_raw, list):
            raise ValueError(f"rule {name!r} 'name_patterns' must be a list")
        name_patterns = tuple(str(p) for p in name_patterns_raw if isinstance(p, str))
        name_regexes_raw = entry.get("name_regexes", [])
        if not isinstance(name_regexes_raw, list):
            raise ValueError(f"rule {name!r} 'name_regexes' must be a list")
        name_regexes = tuple(
            str(pattern) for pattern in name_regexes_raw if isinstance(pattern, str)
        )
        for pattern in name_regexes:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ValueError(
                    f"rule {name!r} has invalid regular expression {pattern!r}"
                ) from exc
        topic_regex_raw = entry.get("topic_regex")
        if topic_regex_raw is not None and not isinstance(topic_regex_raw, str):
            raise ValueError(f"rule {name!r} 'topic_regex' must be a string")
        if isinstance(topic_regex_raw, str):
            try:
                compiled_topic = re.compile(topic_regex_raw)
            except re.error as exc:
                raise ValueError(f"rule {name!r} has invalid 'topic_regex'") from exc
            if "topic" not in compiled_topic.groupindex:
                raise ValueError(f"rule {name!r} 'topic_regex' must capture a named 'topic' group")
        priority = entry.get("priority", 0)
        if not isinstance(priority, int):
            raise ValueError(f"rule {name!r} 'priority' must be an integer")
        always_matches = entry.get("always_matches", False)
        if not isinstance(always_matches, bool):
            raise ValueError(f"rule {name!r} 'always_matches' must be a boolean")
        return OrganizationRule(
            name=name,
            destination=destination,
            extensions=extensions,
            name_patterns=name_patterns,
            name_regexes=name_regexes,
            topic_regex=topic_regex_raw,
            priority=priority,
            always_matches=always_matches,
        )


@lru_cache(maxsize=1)
def get_config_service() -> ConfigService:
    """Process-wide singleton — configuration discovery has no per-call state."""
    return ConfigService()
