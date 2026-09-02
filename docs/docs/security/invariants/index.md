# Security invariants

| Rule doc | Covers |
|---|---|
| [security.md](security.md) | Filesystem safety guarantees, no destructive actions without confirmation, env-var hygiene, secret handling. |

Read [security.md](security.md) before any code path that reads/writes/moves files, loads env vars, or talks to a remote service.