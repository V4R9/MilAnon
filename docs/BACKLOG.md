# MilAnon — Post-MVP Backlog

> Items for iteration after MVP completion.
> Priority: P0 (critical), P1 (next), P2 (soon), P3 (later)
> Status: 🔴 Open, 🟡 In Progress, ✅ Done

---

## Iteration 1 — Done ✅

- B-007: PDF Tables as Markdown ✅
- B-004: Initial.NACHNAME Pattern ✅
- B-005: Municipality Stopwords ✅
- B-006: GEBURTSDATUM context-only ✅
- B-001: GUI Database Reset ✅
- B-002: Documentation Cleanup ✅
- B-003: Real-World Verification ✅

---

## Iteration 2 — Done ✅

- B-008: Generic Name CSV Import ✅
- B-009: Quick-Add Names in GUI ✅

---

## Iteration 2b — Done ✅

- B-008-fix: Combined "Name / Vorname" column format ✅
- B-011: Visual PDF page detection + optional image embed ✅
- "Alle" municipality completely excluded from matching ✅
- "Adj" added as standalone rank ✅
- Per-file progress output in CLI ✅
- Version number in GUI sidebar ✅
- CSV delimiter auto-detection (csv.Sniffer) ✅

---

## Iteration 2c — Done ✅

- B-011-fix: --embed-images rendering PNGs ✅
- B-012: LLM Context Generator with interactive unit selection ✅
- B-012-fix: EINHEIT duplicate normalization + Context output path ✅
- B-011-fix2: Visual page heuristic tightened (AND logic) ✅
- Code Review: All 14 findings addressed (refactoring) ✅

---

## Iteration 4 — Output Quality (from MD Analysis 2026-03-24)

## B-013: Organigramm/Gliederung Pages — Mega-Cell Visual Detection (P1) 🔴

**Problem:** Organigramm Stab and Gliederung pages are visual layouts but only have 3 columns — heuristic doesn't catch them. One cell contains 1000+ chars of garbled content.

**Required Fix:** Add third condition to `_is_visual_layout()`: ANY single cell >500 characters → visual layout.

**Commit:** `fix(parser): detect mega-cell visual layouts (organigramm, gliederung)`

---

## B-014: Remove Empty Columns from PDF Tables (P1) 🔴

**Problem:** Dokumentenbudget has 5 real columns but pdfplumber extracts 15 due to merged cells. Extra columns are empty in every row.

**Required Fix:** Post-processing: remove columns that are empty in ALL rows before Markdown rendering.

**Commit:** `feat(parser): strip empty columns from PDF table extraction`

---

## B-022: EML Display Names Not Anonymized (P1) 🔴

**Problem:** `From: Milo Bärtschi <[EMAIL_178]>` — email anonymized but display name leaks. Systematic problem for ALL EML headers.

**Required Fix:** New EmlDisplayNameRecognizer that extracts display names from From/To/Cc/Bcc headers and creates PERSON entities. Confidence 0.85.

**Commit:** `feat(recognition): anonymize display names in EML From/To/Cc/Bcc headers`

---

## Iteration 7 — De-Anonymization Quality (from Obsidian Test 2026-03-24)

## B-023: De-Anonymize Filenames with Placeholders (P1) 🔴

**Problem:** `[PERSON_005].md` stays as placeholder filename. Should become `Brüngger_Xenia.md`.

**Required Fix:** Scan output filename for placeholders, resolve via MappingService, transform to filesystem-safe `Nachname_Vorname` format.

**Commit:** `feat(deanonymize): resolve placeholders in output filenames`

---

## B-024: Obsidian Wiki-Link Compatibility (P1) 🔴

**Problem:** `[[PERSON_005]]` becomes `[Xenia BRÜNGGER]` (broken link). Should become `[[Brüngger_Xenia|Xenia BRÜNGGER]]`.

**Required Fix:** Process Obsidian `[[PLACEHOLDER]]` links BEFORE regular placeholders. Replace with proper alias format matching B-023 naming.

**Commit:** `feat(deanonymize): handle Obsidian wiki-links with proper alias format`

---

## B-025: In-Place De-Anonymization (P2) 🔴

**Problem:** De-anonymizer always creates a copy. User wants to modify files directly in the Obsidian vault.

**Required Fix:** New `--in-place` flag. Safety: confirmation prompt + optional `.milanon_backup/`.

**Commit:** `feat(deanonymize): add --in-place flag for direct vault de-anonymization`

---

## Iteration 8 — GUI Enhancements (E7 + E10 Foundation)

## B-026: Embed Images Checkbox on Anonymize Page (P1) 🔴

**Discovered in:** GUI testing (2026-03-24)

**Problem:** The CLI has `--embed-images` to render visual PDF pages (WAP/Picasso) as PNG, but the GUI has no corresponding option. Users who only use the GUI cannot access this feature.

**Required Fix:** Add a fourth checkbox to the Anonymize page options row:
- Label: "Embed visual pages as PNG"
- Help text: "Renders WAP/schedule pages as PNG images in the output (NOT anonymized)."
- Pass `embed_images=True` to `uc.execute()` when checked.

**Acceptance Criteria:**
- Given the Anonymize page, when loaded, then an "Embed visual pages as PNG" checkbox is visible alongside Recursive, Force, and Dry run.
- Given the checkbox is checked and a PDF with visual pages is processed, when anonymization runs, then PNGs are generated next to the .md output.
- Given the checkbox is unchecked, when a PDF with visual pages is processed, then only placeholder markers are inserted (existing behavior).

**Commit:** `feat(gui): add embed-images checkbox to Anonymize page`

---

## B-027: LLM Workflow Page — Guided Round-Trip Experience (P1) 🔴

**Discovered in:** UX brainstorming session (2026-03-24)

**Problem:** The GUI has no support for the LLM workflow. The user must manually:
1. Generate a context file via CLI
2. Copy-paste anonymized documents into Claude.ai
3. Copy Claude's output into files
4. Run de-anonymize via CLI

This is error-prone, tedious, and the main reason users fall back to the terminal.

**Vision:** A dedicated "LLM Workflow" page that guides the user through the complete round-trip in a single, intuitive interface. The page grows with Epic E10 (Pack/Unpack) but starts useful from day one.

**Required Fix:**

New navigation entry between "De-Anonymize" and "DB Import":
```python
page = st.sidebar.radio(
    "Navigation",
    ["Anonymize", "De-Anonymize", "LLM Workflow", "DB Import", "DB Stats"],
)
```

The page uses `st.tabs()` with three guided steps:

### Tab 1: "📦 Pack for LLM"

**Section 1a — Context Generator:**
- st.subheader("Step 1: Generate Context")
- st.markdown explaining what the context file does and why it matters
- Unit selector: st.selectbox populated from `GenerateContextUseCase.get_available_units()`
  - Format: "Inf Kp 56/1 (Company)" — shows original value + level
  - If no units in DB: st.info with link to DB Import page
- Output path: st.text_input with sensible default (e.g. last anonymize output dir + "/CONTEXT.md")
- [Generate Context] button
- After generation: show content in st.expander("Preview CONTEXT.md") with st.code(content, language="markdown")
- st.download_button("📥 Download CONTEXT.md", content) — lets user save it anywhere

**Section 1b — Pack Builder (E10.1 Foundation — initially simplified):**
- st.subheader("Step 2: Build Prompt Package")
- Template selector: st.selectbox with options:
  - "Obsidian Notes — Personendossier pro Person mit YAML Frontmatter"
  - "Befehlsentwurf — Kompaniebefehl aus dem Dossier ableiten"
  - "Analyse — Entscheide, Zeitplan, Pendenzen, Risiken"
  - "Freier Prompt — eigene Anweisung"
- If "Freier Prompt" selected: st.text_area("Your prompt", placeholder="z.B. Erstelle mir eine Übersicht der Personalfälle...")
- Anonymized input: st.text_input("Anonymized files folder", placeholder="/path/to/test_output")
- [Build Pack] button
- After build: st.text_area with the complete pack content (Context + Template + Document), readonly
- st.download_button("📥 Download Pack") + st.caption("Copy the content above and paste into Claude.ai")

**Implementation for v1 (before E10.1 is fully built):**
The "Build Pack" button reads CONTEXT.md + all .md files from the input folder, concatenates them with the template instructions, and displays the result. No clipboard API needed — the user copies from the text area.

### Tab 2: "💬 Work with LLM"

**Guided instructions with visual cues:**
```
st.subheader("Send to Claude.ai")

st.markdown("""
### How to use the pack:

1. **Copy** the pack content from Step 1 (or download and open the file)
2. **Open** [Claude.ai](https://claude.ai) in a new tab
3. **Paste** the entire pack as your first message
4. **Work** with Claude — refine, ask follow-up questions, iterate
5. **Copy** Claude's final output when you're satisfied

### Tips:
- Tell Claude to preserve all `[PLACEHOLDER]` tokens exactly as written
- If Claude's response is too long, ask it to split into sections
- For Obsidian Notes: ask Claude to separate each person with `---`
""")

st.info("💡 Coming soon: One-click clipboard integration and prompt templates with auto-fill.")
```

### Tab 3: "📥 Unpack & De-Anonymize"

**Full de-anonymization interface for LLM output:**
- st.subheader("Restore Real Names from LLM Output")
- st.markdown explaining the unpack step

**Input method tabs:** st.radio("Input method", ["Paste text", "Select file/folder"])

**If "Paste text":**
- llm_output = st.text_area("Paste Claude's output here", height=400, placeholder="Paste the complete LLM response...")
- Output path: st.text_input("Save to", placeholder="/path/to/obsidian/vault/Personelles")

**If "Select file/folder":**
- Input path: st.text_input("LLM output file or folder", placeholder="/path/to/llm_output/")
- Output path: st.text_input("Save to", placeholder="/path/to/obsidian/vault/")

**Options row:**
- col1: st.checkbox("Split on --- separators", help="Creates separate files for each section")
- col2: st.checkbox("De-anonymize in-place", help="Overwrites input files directly (requires B-025)", disabled=True) ← disabled until B-025 is implemented

**[De-Anonymize & Save] button:**
1. If paste mode: write to temp file first
2. Run DeAnonymizeUseCase
3. Show results: "Restored N placeholders across M files"
4. Show file list: which files were written where
5. If warnings (unresolved placeholders): show in expander

**Preview section:**
- After de-anonymization, show a preview of the first restored file in st.expander
- st.caption("Check that names are correctly restored before opening in Obsidian")

### UX Polish:

**Progress indicators:**
- Each tab shows a status icon in the tab title: "📦 Pack for LLM", "💬 Work with LLM", "📥 Unpack"
- After completing Step 1, show st.success with arrow: "✅ Pack ready → proceed to Step 2"
- After completing Step 3, show st.balloons() + link to output folder

**Session state:**
- Remember the last used unit, template, input/output paths across tab switches
- If the user already generated a context in Step 1, auto-fill the output path in Step 3

**Error handling:**
- If DB is empty when opening the page: st.warning("No entities in database. Import data first.") with button linking to DB Import
- If no units found: st.info("No units found. Run anonymization first to detect units.")
- If de-anonymization has unresolved placeholders: st.warning with count + expandable list

**Acceptance Criteria:**
- Given the GUI, when "LLM Workflow" is selected, then a page with 3 tabs appears.
- Given units in the DB, when Tab 1 is opened, then the unit dropdown is populated.
- Given a generated context, when "Preview" is clicked, then the full CONTEXT.md content is shown.
- Given pasted LLM output with placeholders, when "De-Anonymize & Save" is clicked, then all placeholders are resolved and files are written.
- Given no entities in the DB, when the page opens, then a helpful message with link to DB Import is shown.
- Given the round-trip workflow (Pack → Claude → Unpack), when all three steps are completed, then de-anonymized files appear in the target folder with correct names.

**Negative Criteria:**
- Must NOT require the terminal for any step of the workflow.
- Must NOT break existing Anonymize/De-Anonymize pages.
- Must NOT send any data over the network — all processing stays local.

**Implementation Order:**
1. Navigation entry + page skeleton with 3 tabs
2. Tab 1: Context Generator (use existing GenerateContextUseCase)
3. Tab 3: Unpack with paste text area (use existing DeAnonymizeUseCase)
4. Tab 1: Pack Builder (simplified v1 — concatenate files)
5. Tab 2: Static instructions
6. UX polish (session state, progress, error handling)

**Commit:** `feat(gui): add LLM Workflow page with context generator, instructions, and unpack`

---

## Iteration 3 — Self-Improving Recognition

## B-010: Post-Anonymization Review — Learn Unknown Names (P2) 🔴

Every document processed makes the tool smarter. After anonymization, scan output for candidate names. User confirms/rejects → confirmed names added to DB automatically.

**Commit:** `feat(review): add post-anonymization review for unknown name candidates`

---

## Iteration 5 — EINHEIT Alias System

## B-018: Military Unit Alias Table (P2) 🔴

**Problem:** Multiple placeholders for same unit due to naming variants.

**Commit:** `feat(mapping): military unit alias table for duplicate EINHEIT resolution`

---

## Iteration 6 — Incremental Processing Improvements

## B-019: Clean Up Orphaned Output Files (P2) 🔴

**Commit:** `feat(cli): add --clean flag to remove orphaned output files`

## B-020: Entity Count Total Across All Outputs (P3) 🔴

**Commit:** `feat(cli): show total entity count across all tracked files in summary`

## B-021: Detect Renamed Files via Content Hash (P3) 🔴

**Commit:** `feat(tracking): detect renamed files via content hash to avoid reprocessing`

---

## Iteration 4b — Recognition Gaps

## B-015: International Phone Numbers (P2) 🔴

**Commit:** `feat(recognition): detect international phone numbers beyond Swiss +41`

## B-016: c/o Name Detection in Address Fields (P2) 🔴

**Commit:** `feat(recognition): detect person names in c/o address prefixes`

## B-017: Near-AHV Warning for Transposed Digits (P3) 🔴

**Commit:** `feat(recognition): warn on possible AHV numbers with transposed digits`

---

## Future Ideas (P3)

- **B-100**: NLP-based entity recognition (spaCy) for unknown names
- **B-101**: Fuzzy matching for typos
- **B-102**: Image OCR in DOCX/PDF for embedded text
- **B-103**: Manual entity management — edit/delete via GUI
- **B-104**: Reporting & Audit trail
- **B-105**: Import summary with delta info
- **B-106**: GUI Finder dialog for folder/file selection (tkinter.filedialog)
- **B-107**: --exclude pattern for anonymize
- **B-108**: CLI UX polish — Kali-Linux-style terminal output
