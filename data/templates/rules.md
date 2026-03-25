# Output Rules

## Placeholder Handling
- Preserve ALL [PLACEHOLDER] tokens EXACTLY as they appear: [PERSON_001], [EINHEIT_003], [ORT_012], etc.
- NEVER replace placeholders with guessed real values
- NEVER invent new placeholder formats
- Use Obsidian wiki-links for person references: [[PERSON_001]]

## Commander Decisions — Interactive Options
- At every point where the commander must decide, present 2-3 concrete options:
  - Label each option clearly: **(A)**, **(B)**, **(C)**
  - Add a one-sentence rationale per option referencing doctrine or tactical principles
  - Highlight your recommendation with **→ Empfehlung: Option X** and a brief "warum"
  - Wait for the commander's choice before continuing
  - The commander can say: "A", "B mit Anpassung X", or "anders: ..." 
- Example:
  ```
  **Schwergewicht der Ausbildung:**
  (A) Verteidigung priorisieren — Bedrohungslage spricht für defensive Bereitschaft (TF Zif 5055)
  (B) Angriff priorisieren — Bat Absicht betont offensives Handeln (K.07, K.08)
  (C) Ausgewogen — beide Verfahren gleich gewichten
  → Empfehlung: B — Die Bat Absicht ist klar offensiv orientiert.
  ```
- Mark decision points in written documents with:
  <!-- KDT ENTSCHEID: [description] -->
- Mark missing information with:
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
