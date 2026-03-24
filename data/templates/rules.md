# Output Rules

## Placeholder Handling
- Preserve ALL [PLACEHOLDER] tokens EXACTLY as they appear: [PERSON_001], [EINHEIT_003], [ORT_012], etc.
- NEVER replace placeholders with guessed real values
- NEVER invent new placeholder formats
- Use Obsidian wiki-links for person references: [[PERSON_001]]

## Decision Markers
- Mark every point where the commander MUST make a personal decision with:
  <!-- KDT ENTSCHEID: [description of what needs to be decided] -->
- Mark every point where information is missing from the input with:
  <!-- FILL: [description of what information is needed] -->

## Output Language
- All output in German (Swiss High German)
- Never use ß — always ss (e.g. Strasse, Grösse, weiss)
- Use correct umlauts: ä, ö, ü
- Military terms remain in their original form (do not translate Fachbegriffe)

## Document Structure
- When producing multiple documents, separate each with --- on its own line
- Start each document with # filename.md as the first line
- Use Markdown formatting consistently

## Doctrine References
- When applying a doctrine principle, cite the source: (BFE Kap X.Y) or (TF Zif XXXX) or (FSO Zif XXX)
- This helps the commander verify your reasoning against the regulation

## Open Questions
- At the end of your output, list any open questions under # Offene Fragen
- These are questions the commander needs to answer before the product is complete

## Quality
- Every statement must be traceable to either the Bat Bf input or doctrine
- Do not invent facts — if information is missing, mark it with <!-- FILL: -->
- Prefer precision over completeness — a partially filled but accurate document is better than a fully filled but speculative one
