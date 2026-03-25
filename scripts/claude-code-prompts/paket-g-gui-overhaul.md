# MEGA-PROMPT: Paket G — Streamlit GUI Overhaul
# MODEL: Opus

## Context
Read CLAUDE.md first. Then read the existing GUI at `src/milanon/gui/app.py` to understand the current structure.
Read `src/milanon/cli/main.py` to see ALL available CLI commands — the GUI must expose the same functionality.
Read `data/doctrine/INDEX.yaml` to understand available workflows.

## Branch
```bash
git checkout -b feat/gui-overhaul
```

## Your Task
Complete overhaul of the Streamlit GUI from 5 pages (v0.3.0) to 9 pages that match the full v0.5.0 feature set.

## Current Pages (keep and update):
1. **Anonymize** — ✅ OK, minor polish only
2. **De-Anonymize** — ✅ OK, minor polish only
3. **LLM Workflow** — ⚠️ NEEDS MAJOR UPDATE (see below)
4. **DB Import** — ✅ OK
5. **DB Stats** — ✅ OK

## Pages to UPDATE:

### LLM Workflow Page — Complete Rewrite
Currently: Only has template selector + free text prompt.
Needs to become the MAIN page with:

```python
st.title("🎯 LLM Workflow")

# Mode selector
col1, col2 = st.columns(2)
with col1:
    mode = st.radio("Modus", ["Berrm", "ADF"], index=0)
with col2:
    unit = st.text_input("Einheit", value="Inf Kp 56/1")

# Workflow selector
workflow = st.selectbox("Workflow", [
    "analyse — Problemerfassung (5+2 Schritt 1)",
    "bdl — Beurteilung der Lage (5+2 Schritt 2)", 
    "entschluss — Entschlussfassung (5+2 Schritt 3)",
    "ei-bf — Einsatzbefehl (5+2 Schritt 5)",
    "wachtdienst — Wachtdienstbefehl",
])

# Input files
input_path = st.text_input("Anonymisierte Dokumente", value="test_output/")
context_path = st.text_input("Kontext (vorherige Schritte)", value="", 
                              help="Pfad zu Vault/Planung/ für Schrittverkettung")

# Pack button
if st.button("📋 Prompt generieren", type="primary"):
    # Call WorkflowPackUseCase
    # Show result in expandable text area
    # Show token estimate
    # Copy to clipboard button

# Also keep the old template-based pack as "Freier Modus" tab
tab1, tab2 = st.tabs(["5+2 Workflow", "Freier Modus"])
```

## Pages to ADD:

### Export Page (NEW)
```python
st.title("📄 DOCX Export")

input_file = st.file_uploader("Markdown-Datei", type=["md"])
# OR text input for path
input_path = st.text_input("Oder Pfad zur Datei")

template = st.selectbox("Vorlage", ["Befehl (Einsatz)", "Befehl (Übung)"])
deanonymize = st.checkbox("De-anonymisieren (Platzhalter → echte Namen)", value=True)

if st.button("📄 DOCX generieren", type="primary"):
    # Call ExportDocxUseCase
    # Offer download button for the .docx
    st.download_button("⬇️ DOCX herunterladen", data=docx_bytes, file_name="befehl.docx")
```

### Doctrine Browser (NEW)
```python
st.title("📚 Doktrin-Datenbank")

# List all doctrine files
# For each: show title, regulation number, key chapters
# Expandable sections to preview extract content
# Button: "Alle Extrakte generieren"
```

### Project Generator (NEW)
```python
st.title("🚀 Claude Project Generator")

unit = st.text_input("Einheit", value="Inf Kp 56/1")
output_dir = st.text_input("Ausgabeordner", value="~/claude_project/")

if st.button("Projekt generieren", type="primary"):
    # Call GenerateProjectUseCase
    # Show generated files
    # Offer ZIP download

st.info("Das generierte Projekt kann direkt in Claude.ai importiert werden.")
```

### Config Page (NEW)
```python
st.title("⚙️ Konfiguration")

mode = st.radio("Standard-Modus", ["Berrm", "ADF"])
unit = st.text_input("Standard-Einheit")
# Save to config on change
```

## Design Guidelines
- Use st.sidebar for navigation (already in place)
- Use consistent emoji prefixes for page titles
- Use st.tabs where a page has multiple modes
- Use st.expander for long content
- Use st.columns for side-by-side layouts
- Use st.status or st.spinner for long operations
- Colors: Use st.success, st.warning, st.error consistently
- KEEP all existing functionality — don't break anything

## Files to modify:
- `src/milanon/gui/app.py` — Complete rewrite of page structure

## Files NOT to touch:
- `src/milanon/cli/main.py`
- `src/milanon/domain/` (any file)
- `src/milanon/usecases/` (any file — call them, don't modify)

## Run and verify:
```bash
source .venv/bin/activate
streamlit run src/milanon/gui/app.py
# Open browser, test every page
python -m pytest tests/ -x --tb=short  # existing tests must pass
```

## Commit
```bash
git add -A
git commit -m "feat(gui): complete Streamlit overhaul — workflow, export, doctrine, project, config pages

- LLM Workflow: 5+2 workflow selector with mode toggle and context chaining
- Export: DOCX generation with de-anonymization and download
- Doctrine Browser: list regulations, preview extracts
- Project Generator: Claude Project ZIP with download
- Config: mode and unit settings
- All existing pages preserved and polished"
```
