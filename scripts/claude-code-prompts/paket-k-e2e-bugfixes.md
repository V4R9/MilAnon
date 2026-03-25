# MEGA-PROMPT: Paket K — Bug Fixes from E2E Testing
# MODEL: Sonnet

## Context
Read CLAUDE.md. We ran a real E2E test with the Bat Dossier and found 3 bugs.

## Branch
```bash
git checkout -b fix/e2e-bugs
```

## Bug 1: {user_unit} not replaced in workflow templates

**Problem:** When running `milanon pack --workflow analyse --unit "Inf Kp 56/1"`, the output still contains literal `{user_unit}` in Layer 4 instead of the unit name or placeholder.

**File:** `src/milanon/usecases/workflow_pack.py`

**Fix:** After loading Layer 4 (the workflow template), replace `{user_unit}` with the unit name. Look at how the existing `PackUseCase` in `pack.py` does it — it already has `template_text.replace("{user_unit}", user_unit)`. Do the same in `WorkflowPackUseCase.execute()` after loading Layer 4.

```python
# After loading layer4 template:
if unit:
    layer4 = layer4.replace("{user_unit}", unit)
```

**Test:** Add a test in `tests/usecases/test_workflow_pack.py`:
```python
def test_user_unit_replaced_in_layer4(self, ...):
    # Verify {user_unit} is replaced with actual unit name in output
```

## Bug 2: Layer 3 (Doctrine Extracts) missing from prompt output

**Problem:** The assembled prompt jumps from Layer 2 (Context) directly to Layer 4 (Task). No doctrine extract content appears in between.

**Investigation:** Check these possible causes:
1. The workflow config in INDEX.yaml might not have `extract:` paths set for the `analyse` workflow
2. The extract files in `data/doctrine/extracts/` might exist but the paths in INDEX.yaml don't match
3. The WorkflowPackUseCase might be loading extracts but they're empty

**Debug steps:**
```python
# Add temporary debug logging or print statements:
# In workflow_pack.py, after loading Layer 3:
print(f"DEBUG Layer 3 parts: {len(layer3_parts)}, total chars: {len(layer3)}")
for ref in wf_config.doctrine:
    print(f"DEBUG doctrine ref: source={ref.source}, extract={ref.extract}")
```

**Files to check:**
- `data/doctrine/INDEX.yaml` — Does `analyse` workflow have `doctrine:` entries with `extract:` paths?
- `data/doctrine/extracts/` — Do the referenced extract files exist?
- `src/milanon/domain/workflow.py` — Does `load_workflows()` correctly parse the `doctrine` section?

**Fix:** Whatever the root cause is, ensure that when running:
```bash
milanon pack test_output/anon/ --workflow analyse --mode berrm --unit "Inf Kp 56/1" --output /tmp/test_prompt.md --no-clipboard
```
The output contains BFE chapter content (e.g., "Initialisierung", "Problemerfassung", "4-Farben") BETWEEN Layer 2 (Context) and Layer 4 (Task).

**Test:** Add a test that verifies doctrine content appears in the assembled prompt.

## Bug 3: CSV files should not be anonymized into output folder

**Problem:** When running `milanon anonymize test_input/ --output test_output/anon/ --recursive`, the PISA CSV (`aw_106f_5664223.csv`) and the personnel helper CSV (`Additional Personell Test File.csv`) are also anonymized and placed in the output folder. These files should only be IMPORTED into the DB, not anonymized and forwarded.

**The issue:** The anonymize command processes ALL files in the input folder recursively. CSV files that are meant for DB import (PISA format, name lists) should be excluded.

**Possible fixes (pick the best one):**

Option A: Add an `--exclude` pattern flag:
```bash
milanon anonymize test_input/ --output test_output/anon/ --recursive --exclude "*.csv"
```

Option B: Add a config/convention — files starting with a prefix are skipped:
Not great — changes user behavior.

Option C: Only anonymize supported document types (PDF, DOCX, EML), skip CSV by default:
```bash
# CSV is excluded by default from anonymize (it's for import, not anonymize)
# Add --include-csv flag if someone really wants to anonymize a CSV
```

**Recommended: Option C** — CSV files are almost always PISA exports or name lists. They're meant for `milanon db import`, not for anonymization. The anonymizer should skip CSV by default.

**File:** `src/milanon/usecases/anonymize.py` — In the file discovery logic, exclude `.csv` and `.xlsx` by default. Add a `--include-spreadsheets` flag to override.

**Also update:** `src/milanon/cli/main.py` — Add the new flag to the `anonymize` command.

**Test:** Add a test that verifies CSV files are skipped by default.

## Bug 4: Pack command includes CSV files in prompt (wastes tokens)

**Problem:** `milanon pack test_output/anon/ --workflow analyse` includes the anonymized CSVs (PISA + personnel list) in the prompt. These are 72 KB of raw tabular data (~18K tokens) that Claude doesn't need for the Analyse workflow. They make up 37% of the total prompt — pure waste.

**File:** `src/milanon/usecases/workflow_pack.py` — look at `_SUPPORTED_INPUT_EXTENSIONS`

**Current:** `_SUPPORTED_INPUT_EXTENSIONS = {".md", ".eml", ".txt", ".csv"}`

**Fix:** Remove `.csv` from the supported extensions in workflow_pack.py. CSVs are import data, not documents to analyze. If someone really needs CSV in a prompt, they can use the classic `milanon pack --template frei` mode.

```python
_SUPPORTED_INPUT_EXTENSIONS = {".md", ".eml", ".txt"}  # CSV excluded — it's for DB import, not LLM prompts
```

**Also fix in:** `src/milanon/usecases/pack.py` — same change to `_SUPPORTED_INPUT_EXTENSIONS`

**Test:** Verify the prompt size drops from ~193K to ~121K chars after this fix.

## Run tests after each fix
```bash
source .venv/bin/activate
python -m pytest tests/ -x --tb=short
```

## Verify the fixes work
```bash
# Bug 1 + 2: Re-run pack and check output
milanon pack test_output/anon/ --workflow analyse --mode berrm --unit "Inf Kp 56/1" --output /tmp/test_prompt.md --no-clipboard
head -100 /tmp/test_prompt.md  # Should show Layer 1, then doctrine content, then task with "Inf Kp 56/1" (not {user_unit})

# Bug 3: Re-run anonymize and check no CSV in output
rm -rf test_output/anon/
milanon anonymize test_input/ --output test_output/anon/ --recursive --embed-images --force
ls test_output/anon/  # Should NOT contain any .csv files
```

## Commit
```bash
git add -A
git commit -m "fix: E2E bugs — {user_unit} replacement, doctrine layer, CSV exclusion from anon+pack

- workflow_pack: replace {user_unit} in Layer 4 templates with actual unit name
- workflow_pack: fix doctrine extract loading (Layer 3 was empty)
- anonymize: skip CSV/XLSX by default (use --include-spreadsheets to override)
- pack: remove .csv from supported input extensions (saves ~37% tokens)
- 4 new tests covering all fixes"
```
