# ADR-008: Incremental Processing (Delta Detection)

## Status
Accepted — 2026-03-23

## Context
The tool processes folders of documents in batch. In real-world usage, the user will re-run the tool on the same folder multiple times as new documents arrive or existing ones change. Processing all files every time is wasteful and slow (especially with OCR on large PDFs).

The same problem exists in both directions:
1. **Anonymization:** Source folder has 100 files. Next week, 20 new files arrive and 5 are modified. Only 25 files need processing.
2. **De-anonymization:** LLM outputs accumulate in a folder. Only new or changed outputs need de-anonymization.

## Options Considered

### Option A: Content hash tracking (SHA-256)
- **Pro:** Detects actual content changes regardless of file metadata (timestamps can be unreliable with cloud sync). Deterministic. Simple to implement. Hash stored in SQLite alongside the processing log.
- **Con:** Requires reading every file to compute hash (but this is fast — hashing 100 files takes milliseconds).

### Option B: Modification timestamp (mtime)
- **Pro:** No need to read file content. Very fast.
- **Con:** Timestamps are unreliable with OneDrive/iCloud sync, Git operations, and file copies. A file may have a new mtime without content changes (or vice versa).

### Option C: No tracking — always reprocess
- **Pro:** Simplest implementation. No state to manage.
- **Con:** Wastes time on unchanged files. OCR on a 70-page PDF takes minutes — doing that unnecessarily is painful.

## Decision
**Option A: Content hash tracking** — SHA-256 hash per file, stored in the `processing_log` table. Combined with a `--force` flag to override when needed.

## Design

### Database Extension

```sql
-- Extend processing_log or create dedicated file tracking table
CREATE TABLE file_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,             -- relative path from input root
    content_hash TEXT NOT NULL,          -- SHA-256 hex digest
    file_size INTEGER NOT NULL,          -- bytes
    operation TEXT NOT NULL,             -- 'anonymize' or 'deanonymize'
    processed_at TEXT NOT NULL,          -- ISO 8601 datetime
    output_path TEXT,                    -- where the output was written
    entity_count INTEGER DEFAULT 0,     -- entities found/replaced
    UNIQUE(file_path, operation)
);
```

### Processing Logic

```
for each file in input_folder:
    current_hash = sha256(file.read_bytes())
    stored = db.get_tracking(file.relative_path, operation)
    
    if stored is None:
        # New file — process it
        process(file)
        db.track(file, current_hash)
    elif stored.content_hash != current_hash:
        # Changed file — reprocess
        process(file)
        db.update_tracking(file, current_hash)
    else:
        # Unchanged — skip
        log.info(f"Skipping {file.name} (unchanged)")
```

### CLI Behavior

```bash
# Default: incremental (only new/changed files)
milanon anonymize ./dossier/ --output ./anon/

# Force reprocess everything
milanon anonymize ./dossier/ --output ./anon/ --force

# Show what would be processed (dry run)
milanon anonymize ./dossier/ --output ./anon/ --dry-run
```

### Output Summary

```
MilAnon — Anonymization Summary
================================
Files scanned:     120
  New:              20  (processed)
  Changed:           5  (reprocessed)
  Unchanged:        93  (skipped)
  Errors:            2  (see log)
Entities found:    347
Duration:          42s
```

### Deleted File Handling

When a source file no longer exists but was previously tracked:
- The anonymized output is NOT automatically deleted (safety measure — never auto-delete).
- The summary reports: "2 previously tracked files no longer found in source."
- A `--clean` flag could remove orphaned outputs (post-MVP).

## Rationale
Content hashing is the most reliable delta detection for this use case. The user's files live on OneDrive (cloud-synced) and local disk — timestamps are unreliable in this setup. SHA-256 hashing is fast (a 100MB file hashes in <100ms) and collision-free for practical purposes.

The `--force` flag ensures the user always has an escape hatch when they want to reprocess everything (e.g., after updating recognition patterns or the entity database).

The `--dry-run` flag lets the user preview what would happen without actually processing — useful for large batches.

## Consequences
- `file_tracking` table added to the database schema.
- `AnonymizeUseCase` and `DeAnonymizeUseCase` check tracking before processing.
- Default behavior is incremental — this is a safe default because it's faster and produces the same result as full processing.
- The `--force` flag overrides tracking and reprocesses all files.
- The `--dry-run` flag shows what would be processed without executing.
- Orphaned outputs (source deleted) are reported but not auto-deleted.
