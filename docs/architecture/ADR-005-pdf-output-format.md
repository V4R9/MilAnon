# ADR-005: PDF Output Format

## Status
Accepted — 2026-03-23

## Context
PDFs cannot be easily modified in-place (especially scanned ones). When a PDF is anonymized, we need to decide what output format to produce.

## Options Considered

### Option A: Markdown (.md)
- **Pro:** Directly consumable by LLMs (Claude, ChatGPT). Preserves headings, lists, tables (as Markdown tables). Lightweight. Easy to edit and inspect.
- **Con:** Loses original PDF formatting (fonts, layout, images).

### Option B: Plaintext (.txt)
- **Pro:** Simplest possible output. No formatting overhead.
- **Con:** Loses all structure — no headings, no tables, no emphasis. LLM gets a wall of text.

### Option C: Recreate PDF
- **Pro:** Output looks like the original.
- **Con:** Extremely complex for scanned PDFs (would require re-rendering OCR text over images). For digital PDFs, in-place text replacement is fragile (depends on PDF internal structure). High implementation effort, low value for the LLM workflow.

## Decision
**Markdown (.md)** — anonymized PDFs are output as Markdown files.

## Rationale
The primary consumer of anonymized documents is an LLM. Markdown is the ideal input format for LLMs — structured, lightweight, and preserving semantic hierarchy (headings, lists, tables). The user confirmed that `.md` is preferred because it can be fed directly into Claude as context.

## Consequences
- `PdfParser` extracts text (or OCR text) and structures it as an `ExtractedDocument`.
- `MarkdownWriter` converts the anonymized `ExtractedDocument` into a `.md` file.
- Original PDF formatting (fonts, colors, exact layout) is not preserved.
- Page breaks from the original PDF are represented as Markdown horizontal rules (`---`).
- Tables detected by pdfplumber are converted to Markdown table syntax.
