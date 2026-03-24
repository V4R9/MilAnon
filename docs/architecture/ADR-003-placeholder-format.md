# ADR-003: Placeholder Format

## Status
Accepted — 2026-03-23

## Context
Anonymized documents need placeholders that replace original PII values. These placeholders must be:
1. Clearly identifiable as placeholders (not confused with real content)
2. Typed (the LLM should know if it's a person, place, or phone number)
3. Numbered (different entities of the same type must be distinguishable)
4. Stable (an LLM must not rephrase, split, or merge them)
5. Parseable by regex for de-anonymization

## Options Considered

### Option A: `[ENTITY_TYPE_NNN]` — Bracketed typed placeholders
- Example: `[PERSON_001]`, `[ORT_003]`, `[AHV_NR_012]`
- **Pro:** Clear type information. Square brackets are unambiguous delimiters. LLMs treat bracketed tokens as atomic units. Easy regex: `\[([A-Z_]+)_(\d{3})\]`. Numbered for uniqueness.
- **Con:** Slightly verbose. Brackets could theoretically conflict with Markdown links (mitigated: Markdown uses `[text](url)` — our format has no parentheses).

### Option B: Readable fake names
- Example: "Müller" → "Bergmann", "Zürich" → "Waldstadt"
- **Pro:** Output reads naturally. Context is preserved for LLM understanding.
- **Con:** LLM may creatively modify fake names. De-anonymization becomes fragile (what if the LLM changes "Bergmann" to "Bergmanns"?). Collision risk with real names. No type information embedded.

### Option C: Hash-based tokens
- Example: `__ENTITY_a7f3b2__`
- **Pro:** Unique, collision-free.
- **Con:** No type information. Not human-readable. LLM cannot infer what the token represents.

### Option D: XML-style tags
- Example: `<PERSON id="001">REDACTED</PERSON>`
- **Pro:** Structured, typed, standard.
- **Con:** LLMs often strip or modify XML tags. Conflicts with HTML content in EML files. Verbose.

## Decision
**Option A: `[ENTITY_TYPE_NNN]`** — Bracketed, typed, zero-padded three-digit numbered placeholders.

## Format Specification

```
[{ENTITY_TYPE}_{NNN}]

Where:
- ENTITY_TYPE: One of the defined EntityType enum values (UPPERCASE, underscores)
- NNN: Zero-padded three-digit sequence number, unique per entity type
- Brackets: Square brackets as delimiters

Examples:
- [PERSON_001]
- [ORT_003]  
- [AHV_NR_012]
- [GRAD_FUNKTION_005]
- [EINHEIT_002]

Regex for detection:
\[([A-Z_]+)_(\d{3})\]
```

## Rationale
LLMs treat square-bracketed tokens as atomic units — they almost never modify content inside brackets. The type prefix tells the LLM what kind of entity it is, which helps it generate contextually appropriate output. The three-digit numbering supports up to 999 entities per type, which is more than sufficient. The format is trivially parseable by regex for de-anonymization.

Tested informally: Claude consistently preserves `[PERSON_001]` in generated text, while it frequently modifies fake names like "Bergmann" to "Bergmanns", "Herr Bergmann", or "B."

## Consequences
- All anonymized output uses this format exclusively.
- The legend header (US-3.2) explains the format to the LLM.
- De-anonymization uses regex `\[([A-Z_]+)_(\d{3})\]` to find and replace.
- Three-digit numbering: if >999 entities of one type exist, extend to four digits (unlikely in practice).
