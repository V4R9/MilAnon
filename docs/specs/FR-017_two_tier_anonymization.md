# FR-017: Two-Tier Anonymization (DSG / DSG+ISG)

> Feature Specification — v1.0
> Date: 2026-03-25
> Status: Approved for Implementation
> Priority: P0 (Changes core product proposition)

---

## 1. Problem Statement

MilAnon currently anonymizes ALL entity types indiscriminately. This over-anonymizes the
input for the LLM, destroying valuable context (unit names, locations, dates) that Claude
needs for meaningful analysis — especially for the dossier-check and analyse workflows.

Legal analysis (ISG Art. 13 i.V.m. Art. 1 Abs. 2) shows that most WK planning data does
NOT meet the INTERN classification threshold. The primary legal obligation is DSG compliance
(protecting personal data), not ISG information protection.

## 2. Solution: Two Anonymization Levels

### Level 1: `dsg` (Default) — Personal Data Protection

Anonymizes only entity types that constitute personal data under DSG Art. 5 lit. a:

| Entity Type | Example | Rationale |
|---|---|---|
| PERSON | "Hptm Marco BERNASCONI" | Personal data (DSG Art. 5 lit. a) |
| VORNAME | "Marco" | Personal data |
| NACHNAME | "BERNASCONI" | Personal data |
| EMAIL | "simon.kohler@mil.admin.ch" | Personal data |
| TELEFON | "079 535 80 46" | Personal data |
| AHV_NR | "756.1234.5678.90" | Personal data (sensitive identifier) |
| GEBURTSDATUM | "15.03.1985" | Personal data |
| ADRESSE | "Bahnhofstrasse 42, 8001 Zürich" | Personal data |
| MEDIZINISCH | "Rückenprobleme" | Besonders schützenswert (DSG Art. 5 lit. c) |
| FAMILIAER | "3 Kinder, verheiratet" | Personal data |
| ARBEITGEBER | "UBS AG" | Personal data (when linked to person) |
| GRAD_FUNKTION | "Hptm BERNASCONI, Kdt Inf Kp 56/1" | Personal data (person identifiable) |

**NOT anonymized in DSG mode:**

| Entity Type | Example | Rationale |
|---|---|---|
| EINHEIT | "Inf Bat 56", "Inf Kp 56/1" | Not personal data; public AO |
| STANDORT_MIL | "WAST", "LUZI", "PASCHGA" | Not personal data; public Waffenplätze |
| ORT | "MELS", "OBERURNEN", "WALENSTADT" | Not personal data; public municipalities |
| FUNKTION | "S4", "VT Of", "Ih Of" | Not personal data when decoupled from person |

### Level 2: `full` — Full Anonymization (current behavior)

Anonymizes ALL entity types including EINHEIT, STANDORT_MIL, ORT, FUNKTION.
Conservative option for INTERN-classified documents.

### Key Design Decision: GRAD_FUNKTION in DSG mode

GRAD_FUNKTION entities like "Hptm BERNASCONI, Kdt Inf Kp 56/1" are anonymized in BOTH
modes because they contain personal data. FUNKTION entities like "S4" (standalone, no name)
are NOT anonymized in DSG mode.

## 3. User Stories

### US-017.1: CLI Level Flag
**As a** company commander using MilAnon CLI,
**I want** to choose between DSG and Full anonymization levels,
**so that** I can balance data protection with LLM context quality.

**Acceptance Criteria:**
- [ ] `milanon anonymize --level dsg` anonymizes only DSG entity types (default)
- [ ] `milanon anonymize --level full` anonymizes all entity types (current behavior)
- [ ] `milanon anonymize` without `--level` defaults to `dsg`
- [ ] Level is stored in file_tracking table for each processed file
- [ ] `--level` flag validation: only `dsg` and `full` are accepted

**Negative Acceptance Criteria:**
- [ ] `--level full` must NOT change any existing behavior (regression-safe)
- [ ] Changing level and re-running does NOT corrupt the mapping database
- [ ] Mixed-level runs (some files DSG, some full) are tracked correctly

### US-017.2: Config Default Level
**As a** commander who always uses DSG mode,
**I want** to set a default level in my configuration,
**so that** I don't have to type `--level dsg` every time.

**Acceptance Criteria:**
- [ ] `milanon config set level dsg` / `full` sets the default
- [ ] CLI `--level` flag overrides config default
- [ ] If neither config nor CLI specifies level, default is `dsg`

### US-017.3: Entity Type Filter
**As a** developer maintaining MilAnon,
**I want** a clean domain-level filter that maps anonymization levels to entity types,
**so that** the filter logic is centralized and testable.

**Acceptance Criteria:**
- [ ] `DSG_ENTITY_TYPES: frozenset[EntityType]` in `entities.py`
- [ ] `ISG_ENTITY_TYPES: frozenset[EntityType]` in `entities.py`
- [ ] `DSG_ENTITY_TYPES | ISG_ENTITY_TYPES == set(EntityType)` (exhaustive)
- [ ] `filter_entities_by_level(entities, level) -> list[DetectedEntity]`
- [ ] Filter in `AnonymizeUseCase` between recognize() and anonymize()
- [ ] RecognitionPipeline and Anonymizer remain unchanged (Open/Closed)

### US-017.4: Context Layer Awareness
**As a** Claude.ai project user,
**I want** the prompt context (Layer 2) to indicate which anonymization level was used,
**so that** Claude knows which entities are real vs. placeholders.

**Acceptance Criteria:**
- [ ] CONTEXT.md includes level explanation
- [ ] `milanon pack --workflow` includes level info in Layer 2

### US-017.5: GUI Level Selection
**Acceptance Criteria:**
- [ ] Radio button: "DSG (recommended)" / "Full (DSG+ISG)"
- [ ] Selection passed to AnonymizeUseCase

### US-017.6: Project Generator Level Awareness
**Acceptance Criteria:**
- [ ] `--level` flag on `milanon project generate`
- [ ] SYSTEM_PROMPT.md explains which data is anonymized

### US-017.7: Review Command Level Awareness
**Acceptance Criteria:**
- [ ] In DSG mode, unit names and locations NOT flagged as leaks
- [ ] In full mode, behavior unchanged

## 4. Edge Cases

| # | Edge Case | Expected Behavior |
|---|---|---|
| EC-1 | Level change on same input | Reprocesses all files |
| EC-2 | Existing DB, switch to DSG | New files use DSG; existing mappings valid |
| EC-3 | GRAD_FUNKTION in DSG mode | Anonymized (contains name) |
| EC-4 | FUNKTION standalone in DSG | NOT anonymized |
| EC-5 | ORT in DSG mode | NOT anonymized |
| EC-6 | Deanonymize on DSG output | Works normally |
| EC-7 | Pack/workflow on DSG output | Works normally |
| EC-8 | Mixed level files | Each file tracks own level |

## 5. Architecture

### 5.1 SOLID Analysis

| Principle | Status | Notes |
|---|---|---|
| S — Single Responsibility | OK | New `anonymization_level.py` owns filter logic |
| O — Open/Closed | OK | Anonymizer and Pipeline unchanged; filter injected |
| L — Liskov | OK | No inheritance changes |
| I — Interface Segregation | OK | No protocol changes |
| D — Dependency Inversion | OK | Filter depends on domain types only |

### 5.2 Dependency Rule

All dependencies point inward. No adapter/infra changes in domain.

## 6. Product Design Implications

### 6.1 DSG Mode = Primary Product
Before: MilAnon = Security tool. After: MilAnon = Privacy tool preserving operational context.

### 6.2 Dossier Check Benefits
DSG mode: "Kdt Inf Kp 56/1 hat Bat Rap am 06.06 um 1600 UND Waf Insp um 1900"
Full mode: "[PERSON_001] hat [EVENT_001] am [DATUM_001]"

### 6.3 Aggregation Risk (ISG Art. 11)
Documented and accepted — commander's decision per ISG Art. 12.

## 7. MoSCoW

**Must:** US-017.1, US-017.3, tests
**Should:** US-017.2, US-017.4
**Could:** US-017.5, US-017.6, US-017.7
**Won't:** Auto-detection (FR-015), per-file override
