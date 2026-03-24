# ADR-001: Language and Runtime

## Status
Accepted — 2026-03-23

## Context
MilAnon is a local CLI tool for document anonymization. The primary user is technically proficient (Python, Java, Git, VS Code on macOS). The tool must parse .eml, .docx, .pdf, .xlsx, .csv files, run OCR, manage a SQLite database, and later support NLP-based entity recognition.

## Options Considered

### Option A: Python 3.11+
- **Pro:** Best-in-class document processing libraries (python-docx, pdfplumber, openpyxl). Tesseract and spaCy are Python-native. Fast development cycle. Claude Code works excellently with Python. No compile step.
- **Con:** Slower runtime than Java. No static type checking at runtime (mitigated by type hints + mypy).

### Option B: Java 17+
- **Pro:** Strong static typing. Apache POI for Office docs, PDFBox for PDFs. Mature ecosystem.
- **Con:** Significantly more boilerplate. No spaCy equivalent. Tesseract integration via JNI is brittle. Slower development cycle. Claude Code support less mature for Java.

### Option C: TypeScript/Node.js
- **Pro:** Good for eventual GUI (Electron). Claude Code supports well.
- **Con:** Document processing libraries are weak compared to Python. OCR integration is painful. Not the user's primary language.

## Decision
**Python 3.11+** with `pyproject.toml` for modern packaging, type hints throughout, and `mypy` for static analysis.

## Rationale
The document processing ecosystem in Python is unmatched. Every library we need (python-docx, pdfplumber, pytesseract, openpyxl, spaCy) is Python-first. The user is comfortable with Python. Claude Code generates excellent Python code. Development velocity is the highest with Python.

## Consequences
- All source code is Python 3.11+.
- Type hints are mandatory on all public interfaces.
- Dependencies managed via `pyproject.toml` with `pip`.
- Tests via `pytest`.
- Code formatting via `ruff` (replaces black + isort + flake8).
- Tesseract and Poppler must be installed separately via `brew` (system dependencies).
