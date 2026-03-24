# ADR-004: Recognition Strategy

## Status
Accepted — 2026-03-23

## Context
The entity recognition engine must detect 16 entity types in German-language military documents. The recognition must be reliable (high recall — minimize missed PII) while keeping false positives manageable. The user has a stable personnel pool (~150 people over 4 years) and processes documents from a known domain (Swiss Army, infantry battalion level).

## Options Considered

### Option A: NLP-only (spaCy German model)
- **Pro:** Handles unknown entities. No manual list maintenance.
- **Con:** German NER models have mediocre accuracy (~75-80% F1 on general text). Military abbreviations and Swiss German confuse general models. Requires downloading a large model (~500MB). Not deterministic.

### Option B: List/Pattern-only (no NLP)
- **Pro:** Deterministic. Fast. High precision on known entities. No model download. Works offline trivially.
- **Con:** Misses truly unknown entities. Requires bootstrapping with personnel data.

### Option C: Three-stage pipeline — Pattern → Military → List (MVP) + NLP (post-MVP)
- **Pro:** Best of both worlds. Pattern matching catches structured PII (AHV, phone, email) with near-100% precision. Military recognizer handles the domain-specific rank+name compound patterns. List recognizer catches all known persons and places. NLP can be added later for residual unknown entities.
- **Con:** More complex architecture than a single-approach solution.

## Decision
**Option C: Three-stage pipeline** with defined priority ordering.

## Pipeline Architecture

```
Input Text
    │
    ▼
┌─────────────────────┐
│ 1. PatternRecognizer │  Regex-based. Highest priority.
│    AHV, phone, email,│  Precise and deterministic.
│    address, dates    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. MilitaryRecognizer│  Domain rules. Second priority.
│    Rank + Name,      │  Understands "Oberstlt i Gst Thomas WEGMÜLLER"
│    Unit designations │  as compound structure.
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. ListRecognizer    │  DB lookup. Third priority.
│    Known names,      │  Matches against mapping DB + reference data.
│    municipalities    │  Case-insensitive, with normalized forms.
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Merge & Deduplicate  │  Resolve overlapping spans.
│                      │  Higher-priority recognizer wins on conflict.
│                      │  Longer match wins at same priority.
└─────────────────────┘
```

## Conflict Resolution Rules

1. **No overlap:** All detected entities are kept.
2. **Partial overlap:** The higher-priority recognizer's entity wins. The lower-priority entity is discarded.
3. **Contained span:** If entity A fully contains entity B, keep A (it's the more complete match).
4. **Same priority, overlapping:** The longer match wins.
5. **Exact same span, same priority:** Keep the first one found (stable ordering).

## Rationale
The three-stage approach matches the data characteristics observed in Phase 0:
- **~30% of entities** are pattern-detectable (AHV numbers, phone numbers, email addresses, dates) — these are the easiest and most critical to never miss.
- **~50% of entities** follow military naming conventions (rank+name, unit designations) — these need domain-specific rules but are highly structured.
- **~20% of entities** are names and places from known lists (personnel DB, Swiss municipalities) — these need lookup but are deterministic once bootstrapped.

This means the MVP pipeline (without NLP) can theoretically catch ~100% of entities in documents about known personnel, which is the primary use case.

## Consequences
- `RecognitionPipeline` orchestrates the three recognizers in order.
- Each recognizer implements the `EntityRecognizer` protocol independently.
- Adding NLP (post-MVP) = adding a 4th recognizer with lowest priority — no existing code changes.
- Adding fuzzy matching = enhancement to `ListRecognizer` — no pipeline changes.
