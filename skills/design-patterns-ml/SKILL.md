---
name: design-patterns-ml
description: >-
  Guides use of common design patterns for Python and ML codebases: when to introduce
  patterns proactively (plugins, registries, facades, factories, callbacks) versus reactively
  after spotting smells (dispatch chains, duplicated SDK code, deep inheritance, train/serve
  duplication). Covers ML platform concerns—contracts, Hydra/config-driven construction,
  Lightning hooks, ETL-to-deploy pipelines, adapters at serving boundaries. Use when
  designing or refactoring non-trivial features, adding extensibility, reviewing code
  smells, or when the user mentions architecture, registry, strategy, facade, or patterns.
---

# Design patterns (Python / ML)

## Default stance

- Prefer **plain functions**, small modules, and **composition** first. Align with the global **python-engineering-standards** rule: patterns are **reactive** to complexity, not mandatory for every file.
- Do **not** over-engineer. If a simpler refactor (extract function, rename, move module) suffices, do that before introducing registries or class hierarchies.
- Do **not** duplicate long prose from python-engineering-standards here—this skill adds **when-to-use** pattern guidance only.

## When to use patterns proactively

Introduce structure **without** waiting for repeated pain when the task clearly demands extensibility or clear boundaries:

| Situation | Pattern / approach |
|-----------|-------------------|
| Multiple implementations behind one concept (losses, samplers, pairing rules, model families, metrics) | **`typing.Protocol` or ABC** + optional **registry** (`dict[str, Callable]` or name → instance); Hydra/OmegaConf targets if the stack uses them |
| Repeated vendor SDK usage (GCS, S3, BigQuery, Vertex, W&B) scattered at call sites | **Facade** or thin **gateway** module; single place for clients, retries, and test doubles |
| Cross-cutting training behavior (logging, EMA, checkpointing, viz) mixed into the training loop | **Hooks / callbacks** (e.g. PyTorch Lightning `Callback`) instead of a growing “god” trainer class |
| Building `nn.Module` graphs or pipelines from typed config | **Factory** or **builder** from dataclasses/YAML; never `eval` on strings |
| Stable contracts between packages or teams | **Protocol** interfaces + explicit data **DTOs** (dataclasses) for inputs/outputs |

## When to suggest patterns reactively (smells)

If you see the smell, suggest the pattern and a minimal fix path:

| Smell | Suggest |
|-------|---------|
| Long `if/elif` / `match` on type or string for behavior | **Strategy**; optionally a **registry** keyed by name |
| Same SDK or URI parsing copy-pasted in many files | **Facade** or **repository/gateway** behind one API |
| Deep inheritance tree only to vary small behaviors | **Composition** + **Strategy** or **Protocol**; fewer subclasses |
| Model/training code importing storage paths and cloud clients everywhere | Move I/O behind **Facade** / **repository**; keep core logic cloud-agnostic |
| Near-duplicate code between training and inference/serving entrypoints | Shared core + **Adapter** at each boundary (batch shape, IO format, device) |
| “One class” that knows data, model, cloud, and CLI | Split responsibilities; use **callbacks** and modules |

## ML platform lens

- **Contracts:** Think in terms of model API, datamodule/dataset boundaries, artifact locations (checkpoints, metrics)—document types, not just dicts.
- **Pipeline mindset:** ETL → train → eval → export → deploy as **stages** with clear inputs/outputs (paths, manifests, URIs), even if not a formal DAG framework yet.
- **Serving vs training:** Same core weights/logic where possible; **adapters** for request format, batching, and hardware at the edge.

## Anti-patterns

- Applying patterns to **trivial** code to look “enterprise.”
- Duplicating the same advice in project rules and this skill—**one source** for “always do X”; link instead.
- Replacing a small `if` with a full registry on the first occurrence.

## In-repo examples (future)

When this or another repo gains **canonical examples** (e.g. a real `Strategy` + registry), add paths under a short **Examples** section here or in `reference.md` beside this file so the agent can jump to code.
