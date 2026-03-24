# Template: Update Dashboard & Notes

You are receiving TWO types of content:

## CURRENT STATE
The first set of documents are RE-ANONYMIZED versions of the user's existing vault notes. These contain the user's manual edits — status changes, notes, checked-off tasks, comments. **PRESERVE ALL OF THIS.**

## NEW INFORMATION
The second set of documents are newly anonymized source materials (emails, reports). These contain new information that should be INTEGRATED into the existing notes.

## Your Task

1. **For each existing person note:** Update with any new information from the new documents. KEEP all existing content (status, notes, pendenzen, korrespondenz). Only ADD new entries.

2. **For new persons** (mentioned in new documents but not in existing notes): Create a new note following the same format as the existing notes.

3. **Update the Dashboard (00_Dashboard.md):**
   - Move persons between status sections (🔴 Offen → 🟡 In Bearbeitung → ✅ Erledigt) if the new information indicates a status change
   - Add new persons
   - Update "Nächster Schritt" if new actions are apparent
   - Update the statistics section

## CRITICAL RULES

- **NEVER delete** existing content from the current state — the user's manual edits are sacred
- **PRESERVE** all [PLACEHOLDER] tokens exactly as written
- **Do NOT** guess or infer real names, locations, or unit designations
- **Separate** each person note with `---` on its own line
- **Use [[PLACEHOLDER]]** for Obsidian wiki-links (double brackets)
- If unsure whether information is new or already known, keep both versions with a note: `<!-- REVIEW: possible duplicate -->`

## Output Format

Output the COMPLETE updated set of notes — dashboard first, then person notes separated by `---`.
