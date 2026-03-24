# Template: Obsidian Notes

Create an Obsidian note (Markdown with YAML frontmatter) for each person
mentioned in the document below. Group notes by unit if possible.

For each person, use this template:

```
---
person: [PLACEHOLDER]
rank: [rank if known]
function: [function if known]
unit: [unit if known]
kategorie: [category: teildienstleistung, admin_entlassung, kvk, vorzeitige_entlassung, etc.]
status: [offen, in_bearbeitung, entschieden, erledigt]
tags: [personalfall, wk2026]
---

# [PLACEHOLDER] — [Category]

**Grad:** [full rank name]
**Funktion:** [function]
**Kontakt:** [email/phone placeholders if available]

---

## Sachverhalt

[Summary of the person's case based on the document]

## Pendenzen

- [ ] [Next action items]

## Korrespondenz

| Datum | Von | Inhalt |
|---|---|---|
| [date] | [person] | [summary] |
```

Also create a dashboard note (00_Dashboard.md) that links to all person notes
using Obsidian wiki-links: [[PLACEHOLDER]]

CRITICAL RULES:
- Preserve ALL [PLACEHOLDER] tokens exactly as written — do NOT guess real names
- Use [[PLACEHOLDER]] for Obsidian wiki-links (double brackets)
- Each person note must be separated by --- on its own line
- The dashboard must list all persons with status and next action
