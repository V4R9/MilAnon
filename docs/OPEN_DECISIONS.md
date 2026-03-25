# Open Decisions — Architecture Decision Log

> Status: Created 2026-03-25.
> Last updated: 2026-03-25 (v0.5.0 complete)

## STATUS: ALL 10 DECISIONS RESOLVED ✅
Resolved on: 25.03.2026

---

## DECIDED ✅ (during this review)

### D-001: Context Window Budget — Passt es?
**Frage:** Passen 5 Layers + ganzes Bat Dossier + Kontext aus vorherigen Schritten in Claude's Context Window?

**Berechnet:**
- Volles Dossier (70 Seiten): ~50K Tokens = 25% von 200K → ✅ Passt
- Nur relevante Seiten: ~22K Tokens = 11% von 200K → ✅ Locker
- Verbleibt für Output: 150K+ Tokens

**Entscheid:** Kein Chunking nötig. Ganzes Dossier kann in einem Call verarbeitet werden.
**ADR:** Nicht nötig — keine Architektur-Änderung.

### D-002: Kontext-Kette — Wächst der Context über die 5 Schritte unbegrenzt?
**Frage:** Step 2 braucht Output von Step 1 als --context. Step 3 braucht Step 1+2. Step 5 braucht alles. Explodiert das?

**Berechnet:**
- Step 1 Output (PE + SOMA + Zeitplan): ~15K chars = ~4K tokens
- Step 2 Output (AUGEZ + Konsequenzen): ~20K chars = ~5K tokens
- Step 3 Output (Varianten + Entschluss): ~15K chars = ~4K tokens
- Step 4 Output (Beso Anordnungen): ~20K chars = ~5K tokens
- Kumulativ für Step 5: ~70K chars = ~18K tokens als Kontext
- Plus Dossier + Layers: ~50K + 18K = ~68K tokens = 34% von 200K → ✅ Passt

**Entscheid:** Kein Summarization nötig. Alle vorherigen Outputs können kumulativ als --context mitgegeben werden.
**Aber:** Wir brauchen ein `--context` das intelligent nur die PRODUKTE inkludiert, nicht den ganzen Vault. Implementierung: `--context vault/Planung/` inkludiert alle .md Files in dem Ordner.

---

## ENTSCHIEDEN ✅ (25.03.2026)

### D-003: Prompt-Sprache — Deutsch oder Englisch?
**Frage:** In welcher Sprache schreiben wir die System Prompts (Layer 1, 4, 5)? Und in welcher Sprache soll Claude antworten?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: Alles Deutsch | Natürlich für Schweizer Kdt, Doktrin ist Deutsch | Claude's Reasoning leicht schwächer auf Deutsch |
| B: Prompts English, Output Deutsch | Besser für Claude's Reasoning | Mischsprache ist verwirrend |
| C: Layer 1+5 English, Layer 3+4 Deutsch, Output Deutsch | Kompromiss: Strukturelle Anweisungen English, Doktrin-Zitate original | Etwas unelegant |

**Empfehlung:** **Option C** — System-Anweisungen (Role, Rules) auf Englisch weil Claude damit besser arbeitet. Doktrin-Auszüge bleiben im deutschen Original (sie zu übersetzen wäre falsch). Aufgabenstellung (Layer 4) auf Deutsch weil die Terminologie stimmen muss. Output auf Deutsch.

**Impact wenn falsch:** Qualität der Outputs leidet, oder Doktrin-Terminologie wird falsch verwendet.

**→ ENTSCHEID: Option C** — Layer 1+5 English, Layer 3+4 Deutsch, Output Deutsch.

### D-004: Default Mode — ADF oder Berrm?
**Frage:** Was ist der Default wenn der User `--mode` nicht angibt?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: Kein Default, --mode ist Pflicht | Zwingt zur bewussten Wahl | Nervt bei jedem Befehl |
| B: Default ADF | Konservativ, klassisch | Könnte für 2026 falsch sein |
| C: Default Berrm | Passt zu 2026 | Könnte für andere Kdt falsch sein |
| D: Default aus Config | `milanon config set mode berrm` pro Projekt | Einmal setzen, dann fertig |

**Empfehlung:** **Option D** — Konfigurierbar pro Projekt. Erster `milanon init` fragt. Danach wird es nie wieder gefragt.

**Impact wenn falsch:** User bekommt falschen Skeleton-Typ und merkt es zu spät.

**→ ENTSCHEID: Option D** — Konfigurierbar pro Projekt via `milanon config set mode berrm`.

### D-005: Vault-Struktur — Was ist kanonisch?
**Frage:** Wir referenzieren `04_Vault/Planung/`, `04_Vault/Dossier/` in der User Journey. Aber das ist nirgends formal definiert. Wo landen die Produkte der einzelnen 5+2-Schritte?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: Flach — alles in einem Ordner | Einfach | Wird unübersichtlich bei 15+ Files |
| B: Nach 5+2-Schritten | `01_problemerfassung/`, `02_bdl/`, ... | Logisch, aber viele Ordner |
| C: Nach Dokumenttyp | `Planung/`, `Dossier/`, `Personelles/` | Natürlicher für den Kdt |

**Empfehlung:** **Option C** — Die Planung-Produkte (PE, BdL, Varianten) in `Planung/`, die finalen Befehle in `Dossier/`, Personalfälle in `Personelles/` (existiert bereits). Das ist wie der Kdt physisch seine Ordner sortieren würde.

```
WK_2026/
  Planung/            ← 5+2 Zwischenprodukte (PE, SOMA, BdL, Varianten, Entschluss)
  Dossier/            ← Finale Befehle (000, 100, 200, 300, 500, EP)
  Personelles/        ← Personalfälle (existiert bereits)
  Ausbildung/         ← Lektionspläne, WAP
  Logistik/           ← Mat-Listen, Bestellungen
```

**Impact wenn falsch:** --context greift ins Leere, unpack legt Files am falschen Ort ab.

**→ ENTSCHEID: Option C** — Nach Dokumenttyp: Planung/, Dossier/, Personelles/.

### D-006: DOCX Round-Trip — Einweg oder Rückweg?
**Frage:** Ist der DOCX-Export ein One-Way-Export (Markdown→DOCX→Drucken), oder soll der User das DOCX editieren und wieder zurück in den Vault bringen können?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: One-Way (Markdown ist Source of Truth) | Einfach, sauber, keine Sync-Probleme | User muss immer im Markdown editieren |
| B: Round-Trip (DOCX editieren → zurück in Markdown) | Flexibel | DOCX→Markdown Konvertierung ist verlustbehaftet, Sync-Hölle |

**Empfehlung:** **Option A** — Markdown bleibt Source of Truth. DOCX ist ein Export-Format. Änderungen werden im Vault gemacht, dann wird neu exportiert. Begründung: DOCX→Markdown ist ein gelöstes Problem (pandoc), aber die Style-Informationen gehen verloren und die Tabellen-Struktur wird kaputt. Nicht den Aufwand wert.

**Impact wenn falsch:** User editiert DOCX, merkt dass Änderungen beim nächsten Export verloren gehen. Frustration.

**→ ENTSCHEID: Option B (Diff-Import)** — Markdown bleibt Source of Truth, aber MilAnon kann Änderungen aus einem editierten DOCX erkennen, als Diff anzeigen, und selektiv ins Markdown zurückspielen. Priorität P2.

### D-007: Wie interagiert der User mit Claude — API oder Chat?
**Frage:** Ruft MilAnon die Claude API direkt auf, oder ist der User der Mittelsmann (Copy-Paste)?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: Copy-Paste (User pastet Prompt in Claude.ai) | Kein API-Key nötig, kostenlos (Pro Plan), einfach | Manuell, fehleranfällig |
| B: API-Call (MilAnon ruft Claude API direkt auf) | Nahtlos, automatisiert | Braucht API-Key, kostet Geld, Abhängigkeit |
| C: Beides optional | Flexibel | Mehr Code zu maintainen |

**Empfehlung:** **Option A als Default, Option B als optionales Feature.** Begründung: Die meisten Miliz-Kdt haben keinen API-Key und wollen keinen einrichten. Copy-Paste in Claude.ai (Pro Plan) ist kostenlos und funktioniert. Für Power-User (wie dich) kann später ein `--api` Flag dazukommen.

**Impact wenn falsch:** Wenn wir API-only bauen, schliesst das 90% der Zielgruppe aus. Wenn wir nur Copy-Paste haben, ist der Flow für Power-User umständlich.

**→ ENTSCHEID: Option A** — Copy-Paste als Default, API später optional.

### D-008: Lizenz — Welche Open Source Lizenz?
**Frage:** MilAnon soll Open Source sein. Welche Lizenz?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| MIT | Maximal permissiv, jeder kann alles | Jemand könnte es kommerziell verkaufen |
| GPL-3.0 | Copyleft, Änderungen müssen offen bleiben | Schreckt Enterprise-User ab |
| Apache-2.0 | Permissiv + Patent-Schutz | Etwas weniger bekannt |
| AGPL-3.0 | Copyleft auch für SaaS | Overkill für ein lokales Tool |

**Empfehlung:** **MIT** — Im Miliz-Kontext will niemand das Tool kommerziell verkaufen. Maximale Permissivität = maximale Verbreitung. Falls ein anderer Kdt das forkt und verbessert, ist das nur gut.

**→ ENTSCHEID NÖTIG**

### D-009: Was wenn das Bat Dossier als reines PDF kommt?
**Frage:** Unsere Anonymisierung funktioniert auf dem extrahierten Text. Aber PDFs mit Tabellen, Karten, Taktischen Zeichen sind schwer zu parsen. Was wenn wichtige Infos in Bildern/Karten stecken?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: Nur Text extrahieren, Bilder ignorieren | Einfach, funktioniert heute | Karteninhalte, Tabellen gehen verloren |
| B: OCR + embed-images (aktueller Ansatz) | Bilder werden eingebettet, Claude kann sie "sehen" | OCR-Qualität variiert, grosse Files |
| C: User extrahiert manuell relevante Seiten | Kontrolle beim User | Aufwand |

**Status:** Option B funktioniert bereits (`--embed-images`). Aber wir haben nie getestet ob Claude die eingebetteten Karten tatsächlich versteht (taktische Zeichen, Abschnittsgrenzen etc.).

**Empfehlung:** **Option B beibehalten, aber im Workflow darauf hinweisen dass Karten-Inhalte manuell in die Problemerfassung einfliessen müssen.** Claude kann Karten nicht zuverlässig lesen — der Kdt muss die taktische Lage aus der Karte selbst interpretieren.

**→ ENTSCHEID: Option A** — Karten sind Sache des Kdt. Claude kann taktische Karten nicht zuverlässig interpretieren. Der Kdt muss die Lageskizze selbst lesen und relevante Informationen in die Problemerfassung einfliessen lassen.

### D-010: Wer schreibt die Doctrine Extracts?
**Frage:** ADR-013 definiert 14 Extract-Files. Werden die automatisch generiert (Script) oder manuell kuratiert?

**Optionen:**
| Option | Pro | Contra |
|---|---|---|
| A: Automatisch (Script sucht Heading-Boundaries) | Schnell, reproduzierbar | Heading-Patterns sind nicht konsistent über alle Reglemente |
| B: Manuell kuratiert | Perfekte Qualität | Aufwand: 14 Files à 30 Min = 7h |
| C: Semi-automatisch (Script + Human Review) | Best of both | Immer noch Aufwand |

**Empfehlung:** **Option C** — Script macht den ersten Cut, Mensch verified. Die BFE-Headings sind relativ konsistent (`## 5.4 Führungstätigkeit:`), aber TF und FSO haben andere Patterns. Einmalig 3-4h Aufwand.

**→ ENTSCHEID: Option C** — Semi-automatisch. Script findet Heading-Boundaries, Mensch reviewed und korrigiert. Geschätzter Aufwand: 3-4h.

### D-008: Lizenz
**Frage:** Welche Open Source Lizenz?

**→ ENTSCHEID: MIT** — Maximal permissiv. Maximale Verbreitung. Reputation als Asset. Repo bleibt vorerst privat, wird bei Bedarf mit MIT-Lizenz veröffentlicht.

---

## IMPLIZITE ANNAHMEN — Müssen validiert werden

### A-001: Claude.ai Pro Plan reicht
**Annahme:** Der User hat einen Claude Pro Plan ($20/Mo) mit genug Nachrichten pro Tag.
**Risiko:** Free Tier hat stark limitierte Nachrichten. Ein 5+2 Durchlauf braucht mindestens 5 Claude-Calls.
**Validation:** Muss im README stehen: "Empfohlen: Claude Pro Plan oder API-Zugang."

### A-002: Der Bat Kdt akzeptiert ein MilAnon-generiertes Dossier
**Annahme:** Ein Befehl der mit LLM-Unterstützung erstellt wurde, wird vom Bat Kdt akzeptiert.
**Risiko:** "Das hast du doch von der KI schreiben lassen" → Reputationsschaden.
**Mitigation:** Die <!-- KDT ENTSCHEID --> Stellen zwingen den Kdt zu eigenen Entscheidungen. Der 5+2-Prozess IST der Beweis dass du gedacht hast. Die Zwischenprodukte (PE, BdL, Varianten) zeigen den Denkweg.

### A-003: Die Doktrin ändert sich nicht vor dem WK
**Annahme:** BFE, TF, FSO, WAT bleiben bis Juni 2026 gültig.
**Risiko:** Neues Reglement oder Weisung der Ter Div ändert Befehlsstruktur.
**Mitigation:** Extracts sind versioniert. Einfach zu updaten.

### A-004: Obsidian ist das richtige Tool
**Annahme:** Der User arbeitet mit Obsidian als Vault.
**Risiko:** Die meisten Miliz-Kdt kennen Obsidian nicht.
**Mitigation:** MilAnon arbeitet mit Plain Markdown. Obsidian-spezifische Features (Wiki-Links) sind optional. Für E16 (Claude Project) und E18 (Starter Kit) braucht der User kein Obsidian.
