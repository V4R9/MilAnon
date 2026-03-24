# Product Requirements Document — MilAnon

> Phase 1 Output — Updated during Phase 3
> Version: 1.1
> Last updated: 2026-03-23

---

## 1. Epics Overview

| Epic | Name | Priority | MVP |
|------|------|----------|-----|
| E1 | Document Ingestion | Must | ✅ |
| E2 | Entity Recognition | Must | ✅ |
| E3 | Anonymization Engine | Must | ✅ |
| E4 | De-Anonymization Engine | Must | ✅ |
| E5 | Mapping Database | Must | ✅ |
| E6 | Reference Data & Bootstrapping | Should | Partial |
| E7 | User Interface | Must | ✅ (CLI + GUI) |
| E8 | LLM Output Optimization | Should | ✅ |
| E9 | Reporting & Audit | Could | ❌ |

---

## 2. Epic E1 — Document Ingestion

**Goal:** Parse supported file formats and extract text content ready for entity recognition.

### US-1.1: Parse EML files

> As a commander, I want to anonymize Outlook email exports (.eml), so that I can use mail content with an LLM without exposing personal data.

**Acceptance Criteria:**
- Given an `.eml` file with `quoted-printable` encoding, when parsed, then the full plaintext body is extracted with correct umlauts (ä, ö, ü).
- Given an `.eml` file with `base64` encoded body, when parsed, then the body is decoded and extracted as readable text.
- Given an `.eml` file with `multipart/alternative` (text + HTML), when parsed, then the plaintext part is preferred.
- Given an `.eml` file, when parsed, then the following header fields are extracted separately: `From`, `To`, `Subject`, `Date`.
- Given an `.eml` file with a signature block containing address, phone, and email, when parsed, then the signature content is included in the extractable text.

**Negative Criteria:**
- The tool must NOT strip or lose email headers — they contain entity-rich data.
- The tool must NOT attempt to render HTML — plaintext extraction only.

**Edge Cases:**
- Forwarded/replied mails with nested MIME parts
- Mails with attachments (extract metadata only, not attachment content in MVP)
- Mails with mixed encodings across parts
- Empty body with subject-only content

### US-1.2: Parse DOCX files

> As a commander, I want to anonymize Word documents (.docx), so that I can use command documents with an LLM.

**Acceptance Criteria:**
- Given a `.docx` file, when parsed, then all paragraph text is extracted in reading order.
- Given a `.docx` file with tables, when parsed, then table cell content is extracted row by row, preserving cell boundaries (e.g. tab-separated or structured).
- Given a `.docx` file with headers and footers, when parsed, then header/footer text is extracted separately and included.
- Given a `.docx` file, when anonymized and de-anonymized, then the output is a valid `.docx` retaining basic formatting (paragraphs, tables, bold/italic).
- Given a `.docx` file containing embedded images, when parsed, then the tool detects the presence and count of images and emits a warning (see US-3.5).

**Negative Criteria:**
- The tool must NOT silently drop table content.
- The tool must NOT modify images or embedded objects.

**Edge Cases:**
- DOCX with tracked changes (extract current state only)
- DOCX with text boxes or shapes containing text
- DOCX with footnotes/endnotes

### US-1.3: Parse PDF files

> As a commander, I want to anonymize PDF documents, including scanned ones, so that I can use command dossiers with an LLM.

**Acceptance Criteria:**
- Given a digital PDF (text layer present), when parsed, then text is extracted using standard text extraction (pdfplumber/pypdf).
- Given a scanned PDF (no text layer), when parsed, then OCR is performed automatically using Tesseract and the recognized text is returned.
- Given a mixed PDF (some pages digital, some scanned), when parsed, then the tool automatically uses the appropriate method per page.
- Given a PDF, when text extraction produces less than 50 characters per page on average, then OCR fallback is triggered automatically.
- Given a PDF, when anonymized, then the output format is Markdown (`.md`), suitable for direct LLM consumption.

**Negative Criteria:**
- The tool must NOT require the user to manually specify whether a PDF is scanned or digital.
- The tool must NOT fail silently on scanned pages — it must either OCR or report the failure.

**Edge Cases:**
- Password-protected PDFs (report error, do not attempt to crack)
- PDFs with embedded fonts causing garbled extraction (trigger OCR fallback)
- Very large PDFs (100+ pages) — must process without excessive memory usage
- PDF portfolios / ZIP-disguised-as-PDF (like the analyzed Befehlsdossier)

### US-1.4: Parse Excel/CSV files

> As a commander, I want to anonymize personnel lists and MilOffice exports (.xlsx, .csv), so that I can analyze personnel data with an LLM.

**Acceptance Criteria:**
- Given a `.csv` file with semicolon or comma delimiter, when parsed, then all rows and columns are correctly extracted.
- Given an `.xlsx` file with multiple sheets, when parsed, then all sheets are processed.
- Given a tabular file with a header row, when parsed, then column headers are preserved and used as context for entity type detection.
- Given a MilOffice export with columns like "Versicherten-Nr", "Name / Vorname", "Grad Kurzform", when parsed, then column semantics are mapped to entity types.

**Negative Criteria:**
- The tool must NOT flatten tabular structure into unstructured text — column associations must be preserved.

**Edge Cases:**
- CSV with inconsistent delimiters
- Excel files with merged cells
- Excel files with formulas (extract computed values, not formulas)
- UTF-8 BOM in CSV files

### US-1.5: Batch ingestion

> As a commander, I want to select multiple files or entire folders for anonymization in one operation, so that I can process a complete command dossier efficiently.

**Acceptance Criteria:**
- Given a folder path, when batch processing is invoked, then all supported files (`.eml`, `.docx`, `.pdf`, `.xlsx`, `.csv`) in the folder are processed.
- Given a folder with subfolders, when batch processing is invoked with recursive flag, then files in subfolders are also processed.
- Given a batch of 50+ files, when processing, then progress is reported per file (filename + status).
- Given a batch where one file fails to parse, when processing, then the error is logged and remaining files continue processing.

**Negative Criteria:**
- A single file failure must NOT abort the entire batch.
- The tool must NOT process unsupported file types silently — it must skip and report them.

---

## 3. Epic E2 — Entity Recognition

**Goal:** Detect sensitive entities in extracted text with high recall (minimize missed PII).

### US-2.1: Recognize entities from known lists

> As a commander, I want the tool to recognize people, places, and units from pre-loaded lists, so that known entities are reliably detected.

**Acceptance Criteria:**
- Given a text containing a name that exists in the mapping database, when recognition runs, then the name is detected regardless of format ("Müller Hans", "Hans Müller", "H. Müller").
- Given a text containing a Swiss municipality from the reference database, when recognition runs, then the municipality is detected.
- Given a text containing a military unit designation matching known patterns, when recognition runs, then the unit is detected.
- Given a text where a known name appears in ALL CAPS (e.g. "WEGMÜLLER"), when recognition runs, then it is matched to the known entity.

**Negative Criteria:**
- The tool must NOT match common German words that happen to also be surnames (e.g. "Gross", "Klein", "Stark") without additional context signals.

### US-2.2: Recognize entities by pattern

> As a commander, I want the tool to detect AHV numbers, phone numbers, email addresses, and other pattern-based entities automatically, so that structured PII is never missed.

**Acceptance Criteria:**
- Given text containing an AHV number in format `756.XXXX.XXXX.XX`, when recognition runs, then it is detected as `AHV_NR`.
- Given text containing a Swiss phone number in any of these formats: `079 535 80 46`, `+41 79 535 80 46`, `0795358046`, when recognition runs, then it is detected as `TELEFON`.
- Given text containing an email address, when recognition runs, then it is detected as `EMAIL`.
- Given text containing a date in formats `dd.mm.yyyy`, `dd.mm.yy`, or `dd. Month yyyy`, when recognition runs, then it is detected as `GEBURTSDATUM` (when contextually a birth date).
- Given text containing a Swiss postal address (street + number + PLZ + city), when recognition runs, then it is detected as `ADRESSE`.

**Negative Criteria:**
- Pattern matching must NOT produce false positives on document reference numbers (e.g. "Dok 1.04-A1" must not be flagged as a phone number).
- Date detection must NOT flag all dates — only dates in personnel context (birth dates, service dates).

**Edge Cases:**
- Phone numbers embedded in running text vs. in structured contact blocks
- Email addresses in EML headers vs. body vs. signature
- AHV numbers with OCR artifacts (e.g. spaces instead of dots)

### US-2.3: Recognize entities by NLP (post-MVP)

> As a commander, I want the tool to detect previously unknown names, organizations, and locations using NLP, so that entities not in any list are still caught.

**Acceptance Criteria:**
- Given text containing a person's name that is NOT in any pre-loaded list, when NLP recognition runs, then it is flagged as a candidate `PERSON` entity with a confidence score.
- Given text containing a location that is NOT in the Swiss municipality database, when NLP recognition runs, then it is flagged as a candidate `ORT`.
- Given a candidate entity with confidence below a configurable threshold (default: 0.7), when recognition runs, then the user is prompted for confirmation.

**Negative Criteria:**
- NLP must NOT run as a network call — all processing must be local (spaCy or similar local model).
- NLP must NOT override a list-based match — lists take priority.

### US-2.4: Fuzzy matching for typos (post-MVP)

> As a commander, I want the tool to catch misspelled names and places, so that typos in documents don't cause PII leaks.

**Acceptance Criteria:**
- Given text containing "Fischerm" where "Fischer" exists in the mapping database, when fuzzy matching runs with a similarity threshold ≥ 0.85, then "Fischerm" is flagged as a candidate match for "Fischer".
- Given a fuzzy match candidate, when the similarity is below 0.95, then the user is prompted to confirm or reject the match.
- Given a fuzzy match that is confirmed by the user, when the same typo appears later, then it is matched automatically without re-prompting.

**Negative Criteria:**
- Fuzzy matching must NOT match short words (< 4 characters) — too many false positives.

### US-2.5: Military-specific entity recognition

> As a commander, I want the tool to understand military naming conventions (rank + name, unit designations), so that military-specific PII patterns are correctly parsed.

**Acceptance Criteria:**
- Given text "Hptm Marco BERNASCONI", when recognition runs, then "Hptm" is detected as `GRAD_FUNKTION` and "Marco BERNASCONI" as `PERSON` (split into `VORNAME` + `NACHNAME`).
- Given text "Oberstlt i Gst Thomas WEGMÜLLER", when recognition runs, then the multi-word rank "Oberstlt i Gst" is correctly parsed as one `GRAD_FUNKTION` entity.
- Given text "Inf Bat 56" or "Inf Kp 56/1" or "Ter Div 2", when recognition runs, then the complete designation is detected as one `EINHEIT` entity.
- Given text "Bat Kdt Stv, Hptm S. MEIER", when recognition runs, then "Bat Kdt Stv" is detected as `FUNKTION`, "Hptm" as `GRAD_FUNKTION`, and "S. MEIER" as `PERSON`.

**Negative Criteria:**
- The tool must NOT split compound unit names (e.g. "Inf Kp 56/1" must not become two entities).
- The tool must NOT confuse military abbreviations with entity types (e.g. "FGG", "WAP", "KVK" are not entity-bearing).

---

## 4. Epic E3 — Anonymization Engine

**Goal:** Replace detected entities with structured, LLM-safe placeholders.

### US-3.1: Replace entities with structured placeholders

> As a commander, I want detected entities replaced with typed, numbered placeholders, so that the anonymized document is LLM-readable and entities are not confused.

**Acceptance Criteria:**
- Given a detected entity "Thomas Wegmüller" of type `PERSON`, when anonymized, then it is replaced with `[PERSON_001]` (or the existing mapping if already known).
- Given the same entity appearing multiple times in one or more documents, when anonymized, then the same placeholder is used consistently.
- Given two different entities of the same type, when anonymized, then they receive different numbers (`[PERSON_001]` vs `[PERSON_002]`).
- Given a `GRAD_FUNKTION` entity "Hptm" preceding a `PERSON` entity, when anonymized, then both are replaced: `[GRAD_FUNKTION_003] [PERSON_001]`.

**Negative Criteria:**
- Placeholders must NOT contain any part of the original value.
- The tool must NOT anonymize content that is not an entity (e.g. general military terminology, tactical descriptions).

### US-3.2: Generate entity legend for LLM context

> As a commander, I want each anonymized document to include a legend header explaining the placeholder types, so that the LLM understands the structure.

**Acceptance Criteria:**
- Given an anonymized document, when generated, then it starts with a legend block listing all placeholder types used and their semantics.
- Given a legend, when read by an LLM, then the LLM understands that `[PERSON_001]` represents a person and must be preserved as-is in outputs.

**Example legend:**
```
--- ANONYMIZATION LEGEND ---
This document has been anonymized. The following placeholders represent sensitive data:
- [PERSON_NNN]: Person names — preserve exactly as written
- [ORT_NNN]: Geographic locations — preserve exactly as written
- [EINHEIT_NNN]: Military unit designations — preserve exactly as written
- [TELEFON_NNN]: Phone numbers — preserve exactly as written
- [EMAIL_NNN]: Email addresses — preserve exactly as written
- [AHV_NR_NNN]: Swiss social security numbers — preserve exactly as written
- [ADRESSE_NNN]: Postal addresses — preserve exactly as written
Do NOT modify, rephrase, or omit any placeholder.
---
```

### US-3.3: Preserve document structure during anonymization

> As a commander, I want the anonymized output to preserve the document's structure (paragraphs, tables, headers), so that context is not lost for the LLM.

**Acceptance Criteria:**
- Given a DOCX with tables, when anonymized, then the output DOCX retains the table structure with placeholders in the appropriate cells.
- Given an EML, when anonymized, then the output preserves the email structure (headers, body, signature separation).
- Given a CSV/XLSX, when anonymized, then the tabular structure is preserved with placeholders in the appropriate cells.
- Given a PDF, when anonymized, then the output is a Markdown (`.md`) file with the anonymized content, preserving headings and paragraph structure where possible.

### US-3.4: Anonymize files in batch

> As a commander, I want to anonymize an entire folder of mixed documents in one operation, so that I can prepare a complete dossier for LLM work.

**Acceptance Criteria:**
- Given a folder with mixed file types, when batch anonymization runs, then each file produces an anonymized output in a designated output folder.
- Given batch processing, when complete, then a summary report lists: files processed, entities found per file, total unique entities, any errors or warnings.
- Given batch processing, when an output folder is specified, then the folder structure of the input is mirrored in the output.

### US-3.5: Warn about embedded images in documents

> As a commander, I want the tool to detect embedded images in documents and warn me, so that I am aware of potential PII in non-text content that cannot be automatically anonymized.

**Acceptance Criteria:**
- Given a DOCX containing embedded images, when anonymized, then the output includes a warning: "⚠ This document contains N embedded image(s). Images are NOT anonymized — please review manually for PII."
- Given a PDF containing embedded raster images (detected via image extraction metadata), when anonymized, then a similar warning is emitted.
- Given batch processing with multiple documents containing images, when the summary report is generated, then it lists all files with image warnings.

**Negative Criteria:**
- The tool must NOT silently ignore embedded images — the user must always be informed.
- The tool must NOT attempt OCR on embedded DOCX images in MVP (this is a post-MVP enhancement).

**Post-MVP Enhancement:**
- Optional `--analyze-images` flag that extracts embedded images, runs OCR, and applies entity recognition to image text content. Detected entities in images are reported for manual review (not auto-replaced in the original image).

---

## 5. Epic E4 — De-Anonymization Engine

**Goal:** Restore original data in LLM outputs by replacing placeholders back to real values.

### US-4.1: De-anonymize LLM output files

> As a commander, I want to feed LLM-generated documents back through the tool to restore real names, places, and data, so that I can use the output directly.

**Acceptance Criteria:**
- Given a Markdown file containing `[PERSON_001]`, when de-anonymized, then the placeholder is replaced with the original value from the mapping database.
- Given a DOCX file from LLM output, when de-anonymized, then all placeholders are replaced while preserving formatting.
- Given a file containing a placeholder that does NOT exist in the mapping database, when de-anonymized, then the placeholder is left as-is and a warning is logged.

**Negative Criteria:**
- De-anonymization must NOT modify any text that is not a recognized placeholder.
- De-anonymization must NOT create a new mapping — it only reads existing mappings.

### US-4.2: Batch de-anonymization

> As a commander, I want to de-anonymize multiple LLM output files at once, so that I can restore a complete set of generated documents.

**Acceptance Criteria:**
- Given a folder of LLM output files (`.md`, `.docx`), when batch de-anonymization runs, then each file is processed and output to a designated folder.
- Given batch de-anonymization, when complete, then a summary lists: files processed, placeholders restored, unresolved placeholders.

---

## 6. Epic E5 — Mapping Database

**Goal:** Persistently store the bidirectional mapping between original values and placeholders.

### US-5.1: Persistent entity mapping

> As a commander, I want entity mappings to persist across sessions, so that "Müller" is always `[PERSON_007]` whether I process a document today or next month.

**Acceptance Criteria:**
- Given an entity mapped in session A, when a new session B encounters the same entity, then the same placeholder is returned.
- Given the mapping database, when inspected, then it stores: entity type, original value, placeholder, first seen date, last seen date, source document.
- Given the database file, when the tool is not running, then the file is a standard SQLite database readable with any SQLite client.

### US-5.2: Import entities from MilOffice/Ada export

> As a commander, I want to bootstrap the entity database from a MilOffice CSV export, so that all my personnel are pre-loaded before the first document processing.

**Acceptance Criteria:**
- Given a MilOffice CSV with columns "Versicherten-Nr", "Name / Vorname", "Grad Kurzform", "Wohnadresse", "Mobiltelefon", when imported, then each row creates entries for: `PERSON`, `VORNAME`, `NACHNAME`, `GRAD_FUNKTION`, `AHV_NR`, `ADRESSE`, `TELEFON`.
- Given an import, when a person already exists in the database, then existing mappings are preserved (no duplicate placeholders).
- Given a CSV with flexible column headers, when imported, then the user can map columns to entity types interactively.

### US-5.3: Manual entity management (post-MVP)

> As a commander, I want to manually add, edit, or delete entity mappings, so that I can correct mistakes or add entities the tool missed.

**Acceptance Criteria:**
- Given the CLI, when I add a manual entity, then it is persisted in the database and used in future processing.
- Given an incorrect mapping, when I edit it, then all future anonymizations and de-anonymizations use the corrected value.
- Given a deleted mapping, when processing future documents, then the entity is treated as unknown (may be re-detected).

### US-5.4: Cross-source entity consistency

> As a commander, I want entities from different sources (PISA import, municipality database, document processing) to map to the same placeholder, so that "Basel" is always `[ORT_001]` regardless of where it was first encountered.

**Acceptance Criteria:**
- Given "Basel" loaded from swiss_municipalities.csv into the reference DB, and a PISA 410 import where a soldier lives in "Basel", when both are processed, then the same `[ORT_NNN]` placeholder is used.
- Given the MappingService, when `get_or_create_placeholder` is called with "Basel" and "BASEL" and "basel", then all three return the identical placeholder (case-insensitive normalization).
- Given a document containing "4058 Basel" processed after a PISA import that also contained "Basel", when anonymized, then the same placeholder is used — not a duplicate.

**Negative Criteria:**
- The tool must NOT create duplicate placeholders for the same entity from different sources.
- The tool must NOT treat "Basel" from PISA and "Basel" from a PDF as different entities.

**Priority:** Must — this is fundamental to data integrity.

---

## 7. Epic E6 — Reference Data & Bootstrapping

### US-6.1: Pre-loaded Swiss municipalities

> As a commander, I want all Swiss municipalities pre-loaded, so that location names are detected without manual configuration.

**Acceptance Criteria:**
- Given the tool installation, when first run, then a database of all Swiss municipalities (BFS open data) is available for matching.
- Given text containing "Walenstadt" or "WALENSTADT", when recognition runs, then it is matched to the municipality database (case-insensitive).

### US-6.2: Military unit pattern library

> As a commander, I want common military unit designation patterns pre-configured, so that units like "Inf Bat 56" are detected automatically.

**Acceptance Criteria:**
- Given text containing "Inf Bat 56", when recognition runs, then it is detected as `EINHEIT` using pattern matching (regex: common prefixes + number patterns).
- Given the pattern library, when a new unit format is encountered, then it can be added to the configuration without code changes.

### US-6.3: Reference data initialization

> As a commander, I want the tool to automatically load Swiss municipalities and military unit patterns into the database on first run, so that entity recognition works immediately without manual setup.

**Acceptance Criteria:**
- Given a fresh installation with no database, when `milanon db init` is run (or the tool is run for the first time), then all ~4'000 Swiss municipalities from `data/swiss_municipalities.csv` are loaded into the `ref_municipalities` table.
- Given a fresh installation, when initialized, then all military rank abbreviations and unit patterns from `data/military_units.csv` are loaded into the `ref_military_units` table.
- Given an already initialized database, when `milanon db init` is run again, then existing data is not duplicated (idempotent operation).
- Given the initialized reference data, when the ListRecognizer runs, then it uses the ref tables for lookups.

**Priority:** Must — without this, entity recognition has no baseline data.

---

## 8. Epic E7 — User Interface

### US-7.1: CLI for anonymization

> As a commander, I want a simple command-line interface to anonymize files, so that I can integrate it into my workflow quickly.

**Acceptance Criteria:**
- Given the command `milanon anonymize <input_path> --output <output_path>`, when executed, then files are anonymized and written to the output path.
- Given the command `milanon anonymize <folder_path> --recursive`, when executed, then all supported files in the folder tree are processed.
- Given processing, when running, then progress is displayed (file name, status, entity count).

### US-7.2: CLI for de-anonymization

> As a commander, I want a simple command to de-anonymize LLM outputs, so that I can restore real data quickly.

**Acceptance Criteria:**
- Given the command `milanon deanonymize <input_path> --output <output_path>`, when executed, then placeholders are replaced with original values.

### US-7.3: CLI for database management

> As a commander, I want CLI commands to manage the entity database, so that I can import, inspect, and maintain mappings.

**Acceptance Criteria:**
- `milanon db import <csv_path>` — imports a MilOffice/Ada export
- `milanon db list [--type PERSON]` — lists known entities, optionally filtered
- `milanon db stats` — shows database statistics (entity counts by type, total mappings)

### US-7.4: Streamlit web GUI

> As a commander, I want a browser-based graphical interface, so that I can anonymize documents, import personnel data, and manage the database without memorizing CLI commands.

**Acceptance Criteria:**
- Given the command `milanon gui`, when executed, then a Streamlit web app opens in the browser.
- Given the GUI, when the "Anonymize" page is open, then I can enter input/output folder paths, select options (recursive, force, dry-run), click "Anonymize", and see a progress bar + summary with entity counts and warnings.
- Given the GUI, when the "De-Anonymize" page is open, then I can enter input/output folder paths and restore documents.
- Given the GUI, when the "PISA Import" page is open, then I can upload a PISA 410 CSV file, it is stored locally under `~/.milanon/imports/`, and I see a summary of imported entities.
- Given the GUI, when the "DB Stats" page is open, then I see entity counts per type, total mappings, and recent processing history.
- Given the GUI, when any operation completes, then all data stays local — the Streamlit app runs on localhost only.

**Negative Criteria:**
- The GUI must NOT send any data to external servers — Streamlit runs 100% locally.
- The GUI must NOT be the only way to use the tool — all features must remain accessible via CLI.

**Priority:** Must — promoted from post-MVP based on stakeholder feedback.

---

## 9. Epic E8 — LLM Output Optimization

### US-8.1: Entity legend header

> (Covered in US-3.2)

### US-8.2: Validate placeholder integrity in LLM output

> As a commander, I want the tool to check if an LLM output has mangled any placeholders, so that I catch problems before de-anonymization.

**Acceptance Criteria:**
- Given an LLM output file, when validation runs, then all `[ENTITY_TYPE_NNN]` patterns are checked against the mapping database.
- Given a placeholder that exists in the file but NOT in the database, when validated, then a warning is raised.
- Given a known placeholder that is MISSING from the output (present in input but absent in output), when validated, then a warning is raised.

---

## 10. MVP Boundary

The **Minimum Viable Product** includes:

| Epic | Included | Notes |
|------|----------|-------|
| E1 — Document Ingestion | ✅ All US | All four file formats + batch |
| E2 — Entity Recognition | ✅ US-2.1, US-2.2, US-2.5 | List-based + pattern + military. NLP (US-2.3) and fuzzy (US-2.4) are post-MVP |
| E3 — Anonymization | ✅ All US incl US-3.5 | Core functionality + image warnings |
| E4 — De-Anonymization | ✅ All US | Core functionality |
| E5 — Mapping Database | ✅ US-5.1, US-5.2, US-5.4 | Persistent mapping + CSV import + cross-source consistency. Manual mgmt (US-5.3) is post-MVP |
| E6 — Reference Data | ✅ US-6.1, US-6.2, US-6.3 | Municipalities + unit patterns + auto-initialization |
| E7 — User Interface | ✅ US-7.1–7.4 | CLI + Streamlit GUI (promoted to MVP) |
| E8 — LLM Optimization | ✅ US-8.2 | Legend + validation |
| E9 — Reporting & Audit | ❌ | Post-MVP |

**MVP Definition of Done:** A commander can:
1. Run `milanon db init` to load Swiss municipalities and military reference data.
2. Import personnel via `milanon db import personnel.csv` (PISA 410 format).
3. Run `milanon anonymize ./dossier/ --output ./anon/` on mixed documents.
4. Work with anonymized outputs in Claude.
5. Run `milanon deanonymize ./llm_output/ --output ./final/` to restore real data.
6. Alternatively, use `milanon gui` for all operations via browser interface.

Entities from all sources (PISA, municipalities, documents) use consistent placeholders.

---

## 11. Decisions Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| D1 | Anonymized PDFs output as `.md` (Markdown) | Directly consumable by LLMs; preserves structure better than `.txt`; PDF recreation is complex and unnecessary for LLM workflow | 2026-03-23 |
| D2 | Embedded images: detect & warn in MVP, optional OCR analysis post-MVP | Full image-OCR pipeline is complex; warning ensures no silent PII leakage; post-MVP `--analyze-images` flag adds opt-in deep analysis | 2026-03-23 |
| D3 | Streamlit GUI promoted from post-MVP to MVP | Stakeholder feedback: CLI is fine for developer, but other commanders need a visual interface. Streamlit runs 100% locally, no data leaves machine. | 2026-03-23 |
| D4 | Cross-source entity consistency is a Must requirement | "Basel" from PISA import, municipality DB, and document processing must always resolve to the same placeholder. Enforced via normalized_value in MappingService. | 2026-03-23 |
| D5 | Automatic reference data initialization on first run | Commanders should not need to manually run setup steps. `milanon db init` or auto-init on first use loads municipalities + military patterns. | 2026-03-23 |
| D6 | Dienstbemerkungen (PISA columns 35-43) are NOT anonymized | Stakeholder decision: these fields are not relevant for anonymization. Simplifies PISA import logic. | 2026-03-23 |

---

## 12. Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | OCR quality on poor scans may miss entities | Allow manual review mode; log low-confidence OCR pages |
| R2 | Context-dependent entity detection (is "Stark" a name or adjective?) | Rank + name pattern helps; flag ambiguous cases for user |
| R3 | LLM may rephrase placeholders (e.g. "Person 001" instead of "[PERSON_001]") | Legend header instructs LLM; validation catches issues |
| R4 | Large documents (100+ pages) may be slow with OCR | Process pages in parallel; show progress |
| R5 | EML MIME parsing edge cases | Use Python `email` stdlib; test with real-world samples |
| R6 | Embedded images in DOCX/PDF may contain PII that is not anonymized | MVP: detect & warn; post-MVP: optional image OCR analysis |
