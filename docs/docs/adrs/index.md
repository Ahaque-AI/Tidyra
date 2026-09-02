# Architectural Decision Records

Every decision that shapes the codebase — layer boundaries, dependency choices, replacement of patterns, public-API name changes — is captured here.

## Index

| ADR | Title | Status | Date |
|---|---|---|---|
| [0001](0001-four-layer-architecture.md) | Four-layer architecture | Accepted | 2026-09-02 |
| [0002](0002-strategy-protocol-for-llm-swap.md) | `OrganizationStrategy` Protocol with future LLM slot | Accepted | 2026-09-02 |
| [0003](0003-uv-only-no-pip-no-venv.md) | uv as the only package manager | Accepted | 2026-09-02 |
| [0004](0004-toml-config-with-discovery-order.md) | TOML configuration with discovery order | Accepted | 2026-09-02 |
| [0005](0005-plan-validator-as-single-safety-gate.md) | `PlanValidator` as the single safety gate | Accepted | 2026-09-02 |
| [0006](0006-importlib-resources-for-packaged-assets.md) | `importlib.resources` for packaged assets | Accepted | 2026-09-02 |
| [0007](0007-tidyra-brand-mark.md) | Tidyra brand mark — folder with three tidied file cards | Accepted | 2026-09-02 |
| [0008](0008-smarter-rule-engine.md) | Smarter rule engine — name patterns, nested destinations, recursive scan | Accepted | 2026-09-02 |
| [0009](0009-cross-platform-packaging.md) | Cross-platform packaging — `flet build` + GitHub Actions releases | Accepted | 2026-09-02 |

## Format

Each ADR uses the MADR-mini template documented in [processes/invariants/processes.md §1](../processes/invariants/processes.md#1-architectural-decisions--adr). Numbering is monotonically increasing; superseded ADRs stay in place with their new status and a link to the replacement.

## Authoring rule

The agent catches architectural decisions and drafts them. The user confirms the wording. See [core/invariants/core.md §4](../core/invariants/core.md#4-agentsmd-is-the-only-meta-doc) and the routing in [AGENTS.md](../../../AGENTS.md).