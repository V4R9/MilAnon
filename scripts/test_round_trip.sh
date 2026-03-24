#!/bin/bash
# MilAnon Round-Trip Test — Full E2E Workflow
# Tests: Import → Anonymize → De-Anonymize (in-place) → Re-Anonymize → Verify
#
# Usage: bash scripts/test_round_trip.sh
#        Run from the project root.
set -e

echo "========================================="
echo "MilAnon Round-Trip Test"
echo "========================================="

cd "$(dirname "$0")/.."
source .venv/bin/activate

WORK_DIR=$(mktemp -d)
echo "Working directory: $WORK_DIR"

# ─── Step 1: Initialize reference data ────────────────────────────────────────
echo ""
echo "--- Step 1: Reset & Initialize ---"
MILANON_DB_PATH="$WORK_DIR/test.db" milanon db init

# ─── Step 2: Import test data ─────────────────────────────────────────────────
echo ""
echo "--- Step 2: Import Test Data ---"
MILANON_DB_PATH="$WORK_DIR/test.db" milanon db import "test_input/Personel Lists/aw_106f_5664223.csv"
MILANON_DB_PATH="$WORK_DIR/test.db" milanon db import "test_input/Personel Lists/Additional Personell Test File.csv" --format names
MILANON_DB_PATH="$WORK_DIR/test.db" milanon db stats

# ─── Step 3: Anonymize ────────────────────────────────────────────────────────
echo ""
echo "--- Step 3: Anonymize ---"
MILANON_DB_PATH="$WORK_DIR/test.db" milanon anonymize "test_input/Personelles Mails" \
    --output "$WORK_DIR/anon" --recursive

# ─── Step 4: Verify anonymization ─────────────────────────────────────────────
echo ""
echo "--- Step 4: Verify Anonymization ---"
ANON_COUNT=$(grep -r "\[PERSON_" "$WORK_DIR/anon" 2>/dev/null | wc -l | tr -d ' ')
echo "Placeholder count in anonymized output: $ANON_COUNT"
if [ "$ANON_COUNT" -eq 0 ]; then
    echo "WARNING: No placeholders found — anonymization may have failed"
    exit 1
fi
echo "OK: Anonymization produced $ANON_COUNT placeholder occurrences"

# ─── Step 5: Simulate LLM output (copy anonymized files as "LLM output") ─────
echo ""
echo "--- Step 5: Simulate LLM Output ---"
mkdir -p "$WORK_DIR/vault"
cp -r "$WORK_DIR/anon/"* "$WORK_DIR/vault/"
echo "Copied anonymized files to vault (simulating LLM output)"

# ─── Step 6: De-anonymize in-place ────────────────────────────────────────────
echo ""
echo "--- Step 6: De-Anonymize In-Place ---"
# Use echo "y" to confirm the in-place prompt non-interactively
echo "y" | MILANON_DB_PATH="$WORK_DIR/test.db" milanon deanonymize "$WORK_DIR/vault" \
    --in-place --force

# ─── Step 7: Verify de-anonymization ──────────────────────────────────────────
echo ""
echo "--- Step 7: Verify De-Anonymization ---"
REMAINING=$(grep -r "\[PERSON_\|\[EMAIL_\|\[TELEFON_" "$WORK_DIR/vault" \
    --include="*.eml" --include="*.md" --include="*.txt" 2>/dev/null | \
    grep -v ".milanon_backup" | wc -l | tr -d ' ')
echo "Remaining placeholders after de-anonymization: $REMAINING"
if [ "$REMAINING" -gt 0 ]; then
    echo "WARNING: $REMAINING placeholder lines remain unresolved"
else
    echo "OK: All placeholders resolved"
fi

# ─── Step 8: Verify backup ────────────────────────────────────────────────────
echo ""
echo "--- Step 8: Verify Backup ---"
if [ -d "$WORK_DIR/vault/.milanon_backup" ]; then
    BACKUP_COUNT=$(find "$WORK_DIR/vault/.milanon_backup" -type f | wc -l | tr -d ' ')
    echo "OK: Backup created — $BACKUP_COUNT files in .milanon_backup/"
else
    echo "FAIL: No backup directory found"
    exit 1
fi

# ─── Step 9: Re-anonymize vault (round-trip) ──────────────────────────────────
echo ""
echo "--- Step 9: Re-Anonymize (Round-Trip) ---"
MILANON_DB_PATH="$WORK_DIR/test.db" milanon anonymize "$WORK_DIR/vault" \
    --output "$WORK_DIR/re-anon" --recursive --force
RE_ANON_COUNT=$(grep -r "\[PERSON_" "$WORK_DIR/re-anon" 2>/dev/null | wc -l | tr -d ' ')
echo "Placeholder count after re-anonymization: $RE_ANON_COUNT"
if [ "$RE_ANON_COUNT" -eq 0 ]; then
    echo "WARNING: Re-anonymization produced no placeholders"
else
    echo "OK: Round-trip complete — $RE_ANON_COUNT placeholder occurrences after re-anonymization"
fi

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "========================================="
echo "Round-Trip Test COMPLETE"
echo "Working directory (inspect manually): $WORK_DIR"
echo "========================================="
