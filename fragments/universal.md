# Engineering standards (global)

Use these when project-specific rules are silent. If `.cursor/rules/project-context.mdc` or `AGENTS.md` conflicts, **prefer the project** for commands and layout; keep the design principles below unless the project explicitly overrides them.

## Tooling and quality gate

- **Formatter/Linter:** Use the project's configured formatter and linter. Fix violations your changes introduce; leave pre-existing violations alone.
- **Type checkers:** If configured, fix only issues your changes introduced.
- **Tests:** If a test suite exists, add or update tests for new behavior; match existing layout, naming, and fixtures.

## Design and code organization

### Architecture

- **Modules over monoliths:** Group related functionality into modules (packages with `__init__.py` exporting the public API). Keep `__init__.py` as a re-export surface, not a place for heavy logic.
- **Thin entrypoints:** CLIs and scripts parse args/config and delegate to library code; avoid business logic in entrypoints.
- **Code reuse:** If the same behavior appears in more than one place, consolidate to one implementation and call it from each site.
- **Single responsibility:** When a function, class, or module grows too large or mixes concerns, split it. When adding types or functions, place them in the module that matches their name and docs; create a new module if nothing fits.
- **YAGNI:** Do not add parameters, base classes, registries, or abstraction layers for hypothetical future needs. Write for what the code does today.

### Functions, classes, and patterns

- **Start with plain functions** as the default unit of organization. When logic branches on types/names repeatedly or one signature cannot express multiple behaviors, consider patterns (Strategy, Registry, etc.)—reactively, not preemptively.
- **Prefer composition over inheritance** unless a subclass clearly specializes behavior from a base.
- **Liskov substitution:** Subtypes must be substitutable for their base. Prefer `Generic[T]` over `object`/`Any` for payloads when it clarifies contracts.
- **Narrow interfaces:** Keep `Protocol` definitions focused on one capability. A type depending on a large Protocol is harder to substitute and test than one depending on a small, focused one. Split a Protocol if callers only ever use part of it.
- **Private helpers in moderation:** Extract a helper when a function is too long and splits naturally, or when logic is reused. Closures inside a function are fine when the helper needs local context and is not reused elsewhere. Avoid monolithic "do everything" functions.

### Naming

- **Concise over verbose:** Names work together with parameters and docstrings; avoid repeating the module or type in every identifier.

### Design patterns (on demand)

- For a **catalog of patterns** (Strategy, registry, Facade, callbacks, adapters, when to use proactively vs after smells) and **ML-platform** guidance, consult the **design-patterns-ml** skill when complexity warrants it — do not treat it as required for every change.
