# Frontend — Flet presentation

The presentation layer is thin: it wires Flet controls to application services. No business logic in handlers, no filesystem calls in views, no domain imports in components.

Start with [invariants/frontend.md](invariants/frontend.md). The rules there are short — most of the "how to add a view" guidance lives in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

- [Invariants](invariants/index.md)
- [frontend.md](invariants/frontend.md)
- [CONTRIBUTING.md](../../../CONTRIBUTING.md) — adding views and components.

## Layout

```
src/tidyra/presentation/
├── app.py            Flet entry point (main, run); wires the brand asset
├── brand.py          Logo path resolver (single source of truth for the mark)
├── controller.py     TidyraApp — view-aware façade over application services
├── state.py          UIState, Screen enum
├── views/
│   ├── home.py       folder picker + scan trigger + brand row
│   ├── preview.py    plan summary + confirm/back
│   └── results.py    done summary
└── components/
    ├── folder_picker.py
    ├── file_list.py
    ├── plan_view.py
    └── result_view.py
```

## Brand assets

The Tidyra logo is `src/tidyra/resources/tidyra-logo.svg`. Resolve the path via `from tidyra.presentation.brand import logo_path` — never hard-code the file path, since `importlib.resources` is what makes the asset discoverable under both editable and frozen installs.