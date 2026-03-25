# MilAnon — Project Summary

> Phase 0 Output — Confirmed by stakeholder
> Last updated: 2026-03-23

## Overview

| Field               | Value |
|---------------------|-------|
| **Project**         | MilAnon — Swiss Military Document Anonymizer & De-Anonymizer |
| **Problem**         | Swiss Army company commanders cannot use public LLMs with operational documents containing PII (names, AHV numbers, addresses, military units). Manual anonymization is impractical at scale (100+ documents per WK cycle). |
| **Goal**            | Local desktop tool that anonymizes sensitive data in documents before LLM processing, and de-anonymizes LLM outputs back to original data. Consistent mapping across sessions and documents over 4-year command periods. |
| **Users**           | Primary: Company commander (Kp Kdt), technically proficient (Python, Git, VS Code). Secondary: Other company commanders (sharing if easily achievable). |
| **Tech Stack**      | Python, macOS, local execution. SQLite for persistent mapping DB. CLI-first with simple GUI (file/folder picker). Claude Max (claude.ai / Claude Code) as primary LLM consumer. |

## Scope

### In Scope

- Anonymization & de-anonymization of: `.eml`, `.docx`, `.pdf`, `.xlsx`/`.csv` files
- OCR fallback for scanned/image-based PDFs (Tesseract, local)
- Entity types: `PERSON`, `VORNAME`, `NACHNAME`, `EMAIL`, `TELEFON`, `AHV_NR`, `GEBURTSDATUM`, `ORT`, `ADRESSE`, `ARBEITGEBER`, `EINHEIT`, `FUNKTION`, `GRAD_FUNKTION`, `MEDIZINISCH`, `FAMILIAER`, `STANDORT_MIL`
- Persistent mapping DB (SQLite), consistent across sessions and documents
- Batch processing (multi-file, multi-folder)
- Fuzzy matching for typo resilience
- Pre-loaded Swiss municipality database (BFS open data)
- Ada/MilOffice CSV import for bootstrapping entity lists
- Structured placeholder format: `[ENTITY_TYPE_NNN]`
- LLM-ready output with entity legend header
- De-anonymization of LLM outputs (primarily `.md` and `.docx`)

### Out of Scope

- Cloud deployment
- Real-time LLM API integration
- Mobile app
- Full NLP model training
- Handwriting recognition

## Constraints

- **All data stays local** — zero network transmission of PII
- macOS primary platform
- Must handle Swiss German text (umlauts, special characters)
- Must handle multiple MIME encodings in `.eml` files (base64, quoted-printable)
- PDF processing must handle both digital and scanned documents

## Definition of Done

User can select a folder of mixed documents, anonymize all in one batch, work with LLM, then de-anonymize the output — with zero PII leakage and consistent entity mapping across sessions.

## Knowledge Base

### Uploaded (in Claude Project Knowledge)

- Befehlsdossier Inf Bat 56 (70-page command dossier, PDF with mixed text/image pages)
- 21 `.eml` files (KVK, Teildienstleistungen, Admin Entlassungen) via Filesystem access
- Obsidian vault with existing person files and dashboard (YAML frontmatter structure)
- MilOffice export sample (header + data row)

### Missing (with mitigation)

| Document | Mitigation |
|----------|------------|
| Full Ada/MilOffice CSV export | Design flexible CSV importer; have sample row for schema |
| Swiss municipality database | Embed open data from BFS/swisstopo at build time |
| Complete military unit designations | Pattern-based recognition + learning from processed documents |

## Entity Patterns (from real data analysis)

| Entity Type | Example Patterns | Detection Challenge |
|-------------|-----------------|---------------------|
| `PERSON` | "Thomas WEGMÜLLER", "Meier, Silvan", "Stefan Brunner" | 3+ name formats across document types |
| `GRAD_FUNKTION` | "Oberstlt i Gst", "Hptm", "Gfr", "Stabsadj" | Always precedes names; variable length |
| `EINHEIT` | "Inf Bat 56", "Inf Kp 56/1", "Ter Div 2" | Structured abbreviation patterns |
| `STANDORT_MIL` | "MELS", "CASTELS", "ST. LUZISTEIG" | Often ALL CAPS; overlap with Swiss places |
| `EMAIL` | "stefan.brunner@gmail.com", "lukas.fischer@milweb.ch" | In headers AND body/signature |
| `TELEFON` | "079 555 67 89", "+41 78 555 43 21", "0795810773" | 3 different formats |
| `ADRESSE` | "Lindenweg 7, 6003 Luzern" | PLZ + Ort as combination |
| `AHV_NR` | "756.9876.5432.10" | Regex: `756\.\d{4}\.\d{4}\.\d{2}` |
| `ARBEITGEBER` | "Brunner Bau AG, Sargans" | Free text, hard to auto-detect |
