# MilAnon — Sprint Plan: Implementation Phase

> Created: 2026-03-25
> Goal: Maximum velocity with parallel Claude Code sessions
> Constraint: 31.03.2026 — Bat Dossier arrives, core workflow must work

---

## Development Strategy: Parallel Claude Code Sessions

### How it works
1. Each "Paket" is a self-contained work package for ONE Claude Code session
2. File-level isolation: No two sessions touch the same file
3. Each session gets a Mega-Prompt with: Goal, Files to touch, Files NOT to touch, Tests to write, Commit message
4. Sessions run in parallel Terminal tabs in VS Code
5. After completion: review, merge, run full test suite

### Branching Strategy
```
main (protected)
├── feat/e14-doctrine-extraction     ← Paket A
├── feat/e15-workflow-infrastructure  ← Paket B
├── feat/e15-workflow-templates       ← Paket C
├── feat/e15-layer-templates          ← Paket D
├── feat/e17-docx-export             ← Paket E
└── feat/e15-cli-integration         ← Paket F (depends on A+B)
```

---

## ROUND 1: Foundation (no dependencies between packages)

### Paket A: Doctrine Chapter Extraction Engine (E14.3)
**Effort:** 3-4h Claude Code
**Branch:** `feat/e14-doctrine-extraction`

**Goal:** Semi-automatic extraction of chapter-level content from full reglemente.

**New files:**
- `src/milanon/usecases/doctrine.py` — DoctrineExtractUseCase
- `src/milanon/cli/doctrine_commands.py` — CLI for `milanon doctrine list|extract`
- `data/doctrine/extracts/*.md` — 14 extract files (output of the script)
- `tests/usecases/test_doctrine.py`

**Files NOT to touch:** Everything in `domain/`, `adapters/`, existing `usecases/`, `cli/main.py`

**What it does:**
1. Reads INDEX.yaml to find which chapters are needed
2. For each extract definition: reads the full .md file, finds heading boundaries, extracts section
3. Writes extract to `data/doctrine/extracts/`
4. CLI: `milanon doctrine list` shows available regulations
5. CLI: `milanon doctrine extract --all` generates all extracts
6. CLI: `milanon doctrine extract --workflow analyse` generates just the ones needed for analyse

**Heading patterns to handle:**
- BFE: `## 5.4 Führungstätigkeit: Beurteilung der Lage` or `# 5.4.2 Herleitung`
- FSO: `### 4.2.4 Beurteilung der Lage` or `## 4.2 Aktionsplanung`
- TF: `## 5.2 Grundsätze der Taktik` or `### 5.2.1 Einsatzgrundsätze`

**Tests:**
- test_extract_bfe_chapter_5_1_returns_initialisierung
- test_extract_fso_chapter_4_2_returns_aktionsplanung
- test_extract_by_workflow_returns_correct_chapters
- test_extract_nonexistent_chapter_raises_error
- test_list_doctrine_returns_all_11_files

---

### Paket B: 5-Layer Prompt Assembly Engine (E15.I1-I2)
**Effort:** 4-5h Claude Code
**Branch:** `feat/e15-workflow-infrastructure`

**Goal:** Extend PackUseCase to support `--workflow` with 5-layer prompt assembly.

**Modified files:**
- `src/milanon/usecases/pack.py` — Add WorkflowPackUseCase (new class, keep old PackUseCase)

**New files:**
- `src/milanon/domain/workflow.py` — WorkflowConfig dataclass, INDEX.yaml parser
- `src/milanon/usecases/workflow_pack.py` — WorkflowPackUseCase
- `tests/usecases/test_workflow_pack.py`
- `tests/domain/test_workflow.py`

**Files NOT to touch:** `domain/entities.py`, `domain/protocols.py`, `adapters/`, `cli/main.py`

**What it does:**
1. Parses INDEX.yaml into WorkflowConfig objects
2. For a given workflow name + mode + step:
   - Layer 1: loads `data/templates/role.md`
   - Layer 2: runs GenerateContextUseCase (existing)
   - Layer 3: loads doctrine extracts from `data/doctrine/extracts/`
   - Layer 4: loads workflow task template from `data/templates/workflows/`
   - Layer 5: loads `data/templates/rules.md`
3. Strips mode markers (<!-- ADF: --> or <!-- BERRM: -->) based on --mode
4. Assembles everything into one prompt text
5. Appends anonymized documents (from --input)
6. Appends previous outputs (from --context)

**Architecture:**
```python
@dataclass
class WorkflowConfig:
    name: str
    description: str
    system_prompt: str  # Layer 4 template filename
    doctrine: list[DoctrineRef]  # source + extract file
    skeleton: str | None  # skeleton filename
    mode_support: list[str]  # ["adf", "berrm"]

class WorkflowPackUseCase:
    def __init__(self, repository, context_generator):
        ...
    
    def execute(
        self,
        workflow: str,        # "analyse", "ei-bf", "wachtdienst"
        mode: str,            # "berrm" or "adf"
        step: int | None,     # 1-5 for 5+2 step selection
        input_path: Path,     # anonymized documents
        unit: str,            # "Inf Kp 56/1"
        context_path: Path | None,  # previous step outputs
        output_path: Path | None,
        copy_clipboard: bool = True,
    ) -> tuple[str, PackResult]:
        ...
```

**Tests:**
- test_parse_index_yaml_returns_all_workflows
- test_assemble_5_layers_includes_all_sections
- test_mode_berrm_strips_adf_markers
- test_mode_adf_strips_berrm_markers
- test_context_path_includes_previous_outputs
- test_workflow_not_found_raises_error
- test_doctrine_extract_missing_raises_clear_error

---

### Paket C: Workflow Task Templates (E15.W1, W4, W5 — pure content, no code)
**Effort:** 2-3h Claude Code
**Branch:** `feat/e15-workflow-templates`

**Goal:** Create the Layer 4 task templates for the 3 priority workflows.

**New files (all under `data/templates/workflows/`):**
- `analyse.md` — 4-Farben-Initialisierung + Problemerfassung + SOMA + Zeitplan
- `ei-bf.md` — 5-Punkte-Befehl aus allen Produkten (references skeleton)
- `wachtdienst.md` — WAT-konformer Wachtdienstbefehl

**Files NOT to touch:** ALL Python code

**What each template contains:**
Each is a Layer 4 prompt (in German, per D-003) that tells Claude exactly:
- What to produce (output format, structure)
- How to structure it (section headers, markdown tables)
- What doctrine to reference (already in Layer 3, but Layer 4 gives task-specific instructions)
- Where the KDT ENTSCHEID markers go
- How to handle mode-specific content (<!-- BERRM: --> / <!-- ADF: -->)

No tests needed — these are content files, not code. But a validation test can check they exist and contain required sections.

---

### Paket D: Layer 1 (Role) + Layer 5 (Rules) Templates (E15.I6-I7)
**Effort:** 1-2h Claude Code
**Branch:** `feat/e15-layer-templates`

**Goal:** Create the static prompt layers that are shared across ALL workflows.

**New files:**
- `data/templates/role.md` — Layer 1: Role definition (English), includes TF 17 tactical competence
- `data/templates/rules.md` — Layer 5: Output rules (English), placeholder preservation, KDT ENTSCHEID

**Files NOT to touch:** ALL Python code

**Content of role.md (Layer 1, English):**
- "You are the staff assistant of a Swiss Army company commander (Stufe Einheit)"
- 5+2 process knowledge
- Einsatzgrundsätze (10 criteria for variant evaluation)
- Taktische Grundsätze (Attack/Defense/Security)
- Taktische Aufgaben (the vocabulary for Absicht + Aufträge)
- Raumordnung (spatial terms)
- Auftragstaktik principle (WAS, nicht WIE)
- "Think 1 level up (Bat), 2 levels down (Gruppe)"

**Content of rules.md (Layer 5, English):**
- Preserve ALL [PLACEHOLDER] tokens exactly
- Mark decisions with <!-- KDT ENTSCHEID: ... -->
- Use Obsidian wiki-links [[PLACEHOLDER]]
- Flag open questions at end
- Reference doctrine sources (BFE Kap X, FSO Zif Y)
- Separate output documents with --- and # filename headers
- Output language: German (Swiss, no ß, always ss)

---

## ROUND 2: Integration (depends on Round 1)

### Paket E: DOCX Export Pipeline (E17.1-5)
**Effort:** 5-6h Claude Code
**Branch:** `feat/e17-docx-export`

**Goal:** `milanon export vault/befehl.md --docx --template befehl_vorlage.docx --deanonymize`

**New files:**
- `src/milanon/usecases/export_docx.py` — ExportDocxUseCase
- `src/milanon/adapters/writers/docx_befehl_writer.py` — Befehl-specific DOCX writer
- `tests/usecases/test_export_docx.py`
- `tests/adapters/writers/test_docx_befehl_writer.py`

**Modified files:**
- `src/milanon/cli/main.py` — add `export` command (ONLY add, don't change existing)

**What it does:**
1. Reads structured Markdown (from Vault)
2. Opens DOCX template (`data/templates/docx/befehl_vorlage.docx`) as base
3. Maps Markdown structure to DOCX styles:
   - `# Grundlagen` → "Heading 1"
   - `### 3 Aufträge` → "1. Main title"
   - `#### 3.1 Z Ambos` → "1.1 Title"
   - `- Bullet` → "Bullet List 1"
   - Aufträge table → Nx2 DOCX table (left=Einheit ~4cm, right=Bullets)
4. If `--deanonymize`: replaces [PLACEHOLDER] → cleartext from DB
5. Saves output DOCX

**Tests:**
- test_export_simple_markdown_creates_docx
- test_heading_styles_mapped_correctly
- test_auftraege_table_creates_nx2_table
- test_deanonymize_replaces_placeholders_in_docx
- test_template_styles_preserved

---

### Paket F: CLI Integration (E15.I1, I3-I5 + CLI wiring)
**Effort:** 3-4h Claude Code
**Branch:** `feat/e15-cli-integration`
**Depends on:** Paket A + B merged

**Goal:** Wire everything together in the CLI: `--workflow`, `--mode`, `--context`, `--step`

**Modified files:**
- `src/milanon/cli/main.py` — add workflow flags to `pack` command, add `doctrine` command group, add `export` command

**What it does:**
1. `milanon pack --workflow analyse --mode berrm --unit "Inf Kp 56/1" --input anon/`
   → calls WorkflowPackUseCase
2. `milanon pack --workflow ei-bf --mode berrm --context vault/Planung/ --input anon/`
   → includes previous outputs
3. `milanon pack --workflow ei-bf --step 5`
   → only the Befehlsgebung step
4. `milanon doctrine list`
   → shows available regulations
5. `milanon doctrine extract --all`
   → generates all chapter extracts
6. `milanon export vault/befehl.md --docx --deanonymize`
   → DOCX generation

**Tests:**
- test_cli_pack_workflow_flag_calls_workflow_pack
- test_cli_pack_mode_flag_passes_through
- test_cli_pack_context_flag_passes_path
- test_cli_doctrine_list_shows_output
- test_cli_export_docx_creates_file

---

## ROUND 3: Content + Polish (after Round 2 merged)

### Paket G: Additional Workflows (E15.W2, W3, W6, W7)
- `data/templates/workflows/bdl.md` — AUGEZ + AEK
- `data/templates/workflows/entschluss.md` — Varianten + Einsatzgrundsätze
- `data/templates/workflows/ep-halten.md` — EP Halten Standort
- `data/templates/workflows/ep-interessenraum.md` — EP Kampf

### Paket H: CLAUDE.md Update + README Overhaul
- Update CLAUDE.md with new commands, architecture, workflow system
- Update README.md with full user documentation
- Update CHANGELOG.md

### Paket I: GUI Update (Streamlit)
- Add Workflow selector to LLM Workflow page
- Add Mode toggle (ADF/Berrm)
- Add Export page
- Add Doctrine browser page

### Paket J: Project Config System
- `milanon config set mode berrm`
- `milanon config set unit "Inf Kp 56/1"`
- `milanon init` — project structure initialization
- Config stored in `.milanon/config.yaml` per project

---

## Execution Plan

### Tag 1 (heute): Round 1 — 4 parallele Sessions
```
Terminal 1: Paket A (Doctrine Extraction)     → 3-4h
Terminal 2: Paket B (Workflow Pack Engine)     → 4-5h
Terminal 3: Paket C (Workflow Templates)       → 2-3h
Terminal 4: Paket D (Layer 1 + 5 Templates)   → 1-2h
```
Alle 4 sind UNABHÄNGIG — keine File-Konflikte.

### Tag 2: Review + Round 2 — 2 parallele Sessions
```
Morning:    Review Round 1, merge alle 4 Branches → main
Terminal 1: Paket E (DOCX Export)              → 5-6h
Terminal 2: Paket F (CLI Integration)          → 3-4h
```
Paket F braucht A+B gemerged. Paket E ist unabhängig.

### Tag 3: Final Integration + Test
```
Morning:    Review Round 2, merge
Terminal 1: Paket H (CLAUDE.md + README)       → 2h
Terminal 2: Paket G (Additional Workflows)     → 3h
Afternoon:  Full test suite, E2E test mit echtem Bat Dossier
Evening:    Release v0.5.0
```

---

## File Conflict Matrix (Round 1)

| File | Paket A | Paket B | Paket C | Paket D |
|---|---|---|---|---|
| `usecases/doctrine.py` | ✏️ CREATE | | | |
| `usecases/workflow_pack.py` | | ✏️ CREATE | | |
| `domain/workflow.py` | | ✏️ CREATE | | |
| `cli/doctrine_commands.py` | ✏️ CREATE | | | |
| `data/doctrine/extracts/*.md` | ✏️ CREATE | | | |
| `data/templates/workflows/*.md` | | | ✏️ CREATE | |
| `data/templates/role.md` | | | | ✏️ CREATE |
| `data/templates/rules.md` | | | | ✏️ CREATE |
| `tests/usecases/test_doctrine.py` | ✏️ CREATE | | | |
| `tests/usecases/test_workflow_pack.py` | | ✏️ CREATE | | |
| `tests/domain/test_workflow.py` | | ✏️ CREATE | | |
| `cli/main.py` | ❌ DON'T | ❌ DON'T | ❌ DON'T | ❌ DON'T |
| `domain/entities.py` | ❌ DON'T | ❌ DON'T | ❌ DON'T | ❌ DON'T |

✏️ = creates new file, ❌ = must not touch
**Zero conflicts in Round 1** — all 4 sessions create NEW files only.
