# Ecosystem: How genero-tools Connects

```
                        ┌─────────────────────────────────────┐
                        │   electRa/Castle Codebase           │
                        │       ~/work/genero                 │
                        │  3.5M+ LOC · 3,400 .4gl files       │
                        └─────────────────┬───────────────────┘
                                          │ scanned by
                                          ▼
┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
│                                                                               │
│  ┌════════════════════════════════════════════════════════════════════════┐   │
│  ║  genero-tools                                                         ║   │
│  ║  ★ THIS REPO ★                                                        ║   │
│  ║                                                                        ║   │
│  ║  • Function signatures, parameters, return types                       ║   │
│  ║  • Call graph analysis (cross-file resolution)                         ║   │
│  ║  • Schema impact analysis (table → function mapping)                   ║   │
│  ║  • Code quality metrics (complexity, LOC, dead code)                   ║   │
│  ║  • Type resolution (LIKE references → actual types)                    ║   │
│  ║  • Module dependencies (.m3 makefiles)                                 ║   │
│  ║                                                                        ║   │
│  ║  Produces: workspace.db · modules.db · workspace.json                  ║   │
│  ║  Interface: query.sh <command> [args]                                  ║   │
│  ╚════════════════════════════════════════════════════════════════════════╝   │
│                                                                               │
└─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
          │                         │                         │
          │ queried via             │ databases               │ analysis used
          │ $GENERO_TOOLS_PATH      │ consumed by             │ to build
          ▼                         ▼                         ▼
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│    genero-vim         │   │    electra-vault      │   │ electra-documentation │
│                       │   │                       │   │                       │
│  • Go to def          │   │  • ~25,800 fn pages   │   │  • Agent used         │
│  • Find refs          │   │  • ~905 schema pages  │   │    query.sh to        │
│  • Autocomplete       │   │  • ~810 module pages  │   │    understand the     │
│  • Hover sigs         │   │  • Cross-linked vault │   │    codebase and write │
│  • Telescope          │   │                       │   │    system docs        │
└───────────────────────┘   └───────────┬───────────┘   └───────────────────────┘
                                        │
                                        │ also consumes
                                        ▼
                            ┌───────────────────────────┐
                            │ agent-knowledge-repository │
                            │ (AKR)                      │
                            │                            │
                            │ • codebase-intelligence    │
                            │   steering file teaches    │
                            │   agents to combine        │
                            │   akr-fetch + query.sh     │
                            └────────────────────────────┘
```

## Role in the Ecosystem

genero-tools is the **structural intelligence layer** (Tier 1) — it parses the raw codebase into queryable databases that power IDE features, documentation generation, and knowledge graph construction.

## Connections

| Repo | Relationship |
|------|-------------|
| **genero-vim** | The vim plugin calls `query.sh` for all code intelligence: go-to-definition, find references, autocomplete, function signatures, Telescope pickers |
| **electra-vault** | The vault generator reads `workspace.db` and `modules.db` to produce function, schema, and module pages (~27,500 pages total) |
| **electra-documentation** | AI agents used genero-tools analysis to understand the codebase structure when producing system documentation |
| **agent-knowledge-repository** | AKR's `codebase-intelligence` steering file teaches agents to combine `akr-fetch` with `query.sh` for structural + experiential context |

## Three-Tier Knowledge Model

```
Tier 1 (Structure)     genero-tools     → functions, calls, schema, metrics  ★ THIS REPO
Tier 2 (Experience)    AKR              → patterns, decisions, bug fixes, gotchas
Tier 3 (Business)      electra-docs     → architecture, data flows, integrations
                              │
                              ▼
                       electra-vault     → unified interlinked graph
```
