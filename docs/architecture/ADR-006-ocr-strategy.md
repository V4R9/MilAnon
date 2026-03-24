# ADR-006: OCR Strategy

## Status
Accepted — 2026-03-23

## Context
Military documents frequently exist as scanned PDFs (printed, distributed, re-scanned). The tool must handle these without manual user intervention.

## Options Considered

### Option A: Tesseract OCR (local, open source)
- **Pro:** Runs locally (no data leaves the machine). Free. German language support. Well-established Python bindings (pytesseract). Excellent quality on printed text.
- **Con:** Requires system installation (`brew install tesseract`). Slow on large documents. Poor on handwriting (not relevant here).

### Option B: Cloud OCR (Google Vision, AWS Textract)
- **Pro:** Higher accuracy on complex layouts. Table detection built-in.
- **Con:** **Violates core constraint** — sends PII to cloud. Non-starter.

### Option C: No OCR — require digital PDFs only
- **Pro:** Simplest implementation.
- **Con:** Excludes a significant portion of real-world military documents. The analyzed Befehlsdossier was effectively image-based.

## Decision
**Tesseract OCR** with automatic fallback. The tool detects whether a PDF page has extractable text; if not (or if extraction yields <50 chars/page), it automatically rasterizes the page and runs OCR.

## Fallback Logic

```
for each page in PDF:
    text = extract_text(page)  # pdfplumber
    if len(text.strip()) < 50:
        image = rasterize_page(page, dpi=300)  # pdf2image
        text = ocr(image, lang='deu')  # pytesseract
        log_warning(f"Page {n}: OCR fallback used")
    yield text
```

## Consequences
- Tesseract + German language pack must be installed: `brew install tesseract tesseract-lang`
- Poppler must be installed for pdf2image: `brew install poppler`
- README documents these system dependencies clearly.
- OCR pages are logged so the user knows which pages used fallback (and may have lower accuracy).
- DPI setting (default 300) is configurable for quality/speed tradeoff.
