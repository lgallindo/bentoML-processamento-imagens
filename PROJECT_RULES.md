# Project Specific Rules — `bentoML-processamento-imagens`

## Educational siblings (`XX_NAME`)

| Rule ID | Rule |
| :--- | :--- |
| **EDU-001** | Each class sample under `XX_NAME/` (e.g. `01_corpus_histograms_model`, `02_grayscale_request_logging`) is a **fully independent** runnable tree: own `service.py`, deps, samples, scripts, README, and tests. |
| **EDU-002** | **No cross-lesson coupling in docs or code.** Do not link, import, symlink, or instruct students to open another `XX_*` folder. No “continuação em…”, “ver lição N”, or relative links like `../02_…`. |
| **EDU-003** | Conceptual reuse is fine only by **copying** code into the sibling; never by depending on a sibling path at runtime or in student-facing prose. |
| **EDU-004** | The repository root remains lesson 0 (baseline). Siblings must not modify root `service.py` behavior to “share” logic. |
| **EDU-005** | Inference routes use `/inference-{op}` (`grayscale`, `blur`, `resize`). Monitor/report routes use `/monitor-{pipeline}-{dataset}-{repr}` (kebab-case). Representations are `-json`, `-csv`, `-image` — never a file extension in the path. |
| **EDU-006** | Every `XX_*/README.md` is a **class handout** with exactly three top-level sections after the title: **Objectivo**, **Comparação com a base**, **Utilização**. “Base” means the **repository root** (lesson 0). Code diffs MUST be inlined AS-IS / TO-BE snippets (no `../…` links to root or to other siblings). Optional short “conceitos” may live under Utilização only when required to operate the APIs. |

## Related

- Workspace research disk: `~/code/research/PROJECT_RULES.md` (**DISK-001**: `.lake` untouchable)
- Universal agent protocol: `~/code/AGENTS.md`
