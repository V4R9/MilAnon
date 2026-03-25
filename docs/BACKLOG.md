# MilAnon — Backlog v3 (Post E2E-Test, 25.03.2026)

> Priorisierung: P0 = Blocker für 31.03, P1 = Wichtig für WK, P2 = Nice-to-have, P3 = Zukunft
> Status: ✅ Done, 🔧 In Progress, ❌ Open, 🐛 Bug

---

## BUGS (aus E2E-Test 25.03.2026)

| ID | Bug | Severity | Status |
|---|---|---|---|
| BUG-001 | `{user_unit}` nicht ersetzt in Workflow-Templates (Layer 4) | 🔴 | ✅ Fixed (Paket K) |
| BUG-002 | Layer 3 (Doctrine Extracts) fehlte im Prompt-Output | 🔴 | ✅ Fixed (Paket K) |
| BUG-003 | CSVs (PISA, Hilfsliste) werden anonymisiert in Output-Ordner | 🟡 | ✅ Fixed (Paket K) |
| BUG-004 | CSVs werden in den Prompt gepackt (37% Token-Verschwendung) | 🟡 | ✅ Fixed (Paket K) |
| BUG-005 | DOCX Writer: `**bold**` wird nicht konvertiert, bleibt als Markdown | 🔴 | ❌ Open |
| BUG-006 | DOCX Writer: `---` Trennlinien werden als leere Paragraphen gerendert | 🟡 | ❌ Open |
| BUG-007 | DOCX Writer: `<!-- FILL: -->` und `<!-- KDT ENTSCHEID: -->` als sichtbarer Text | 🟡 | ❌ Open |
| BUG-008 | DOCX Writer: `> Blockquotes` nicht erkannt | 🟡 | ❌ Open |
| BUG-009 | DOCX Writer: Tabellen mit >2 Spalten werden falsch geparst | 🔴 | ❌ Open |
| BUG-010 | DOCX Writer: Keine Absatzabstände — alles klebt zusammen | 🟡 | ❌ Open |
| BUG-011 | DOCX Writer: Aufträge-Tabelle (Pt 3) vs. Info-Tabellen nicht differenziert | 🟡 | ❌ Open |
| BUG-012 | PII-Leaks: Einzelne Vor-/Nachnamen ohne Rang werden nicht erkannt (Ciardo, Megevand, Nicolas, Stéphane, Etienne) | 🟡 | ❌ Open |
| BUG-013 | PII-Leaks: Strassennamen ohne "strasse"/"weg" werden nicht als Adressen erkannt (Fesenacker 3, Avenue D'Aire 73, Tumma 9) | 🟡 | ❌ Open |
| BUG-014 | Project Generator: Anonymisiertes Dossier fehlt im Output | 🔴 | ✅ Fixed (Paket L) |
| BUG-015 | Project Generator: INSTRUCTIONS.md + SYSTEM_PROMPT.md verwirrend (2 Files, nur 1 Feld in Claude.ai) | 🟡 | ✅ Fixed (Paket L) |
| BUG-016 | Project Generator: CHEAT_SHEET.md nicht im Output | 🟡 | ✅ Fixed (Paket L) |
| BUG-017 | Project Generator: PNGs (WAP) nicht im Output | 🟡 | ✅ Fixed (Paket L) |
| BUG-018 | Rich CLI Output fehlt bei `pack --workflow` (zeigt altes Format statt Rich Panels) | 🟡 | ❌ Open |

---

## FEATURE REQUESTS (aus heutiger Session)

### FR-001: Dossier Quality Check (Pre-Flight Validation) — P0
**Beschreibung:** Vor der Aktionsplanung das Bat Dossier auf Logikfehler, fehlende Infos, Inkonsistenzen und Widersprüche prüfen.
**Workflow:** `milanon pack --workflow dossier-check` oder im Claude Project: "Prüfe mein Bat Dossier"
**Template:** `data/templates/workflows/dossier-check.md` — ✅ Erstellt
**Prüfbereiche:**
- Terminprüfung (WAP vs. Befehle: Überlappungen, verstrichene Fristen)
- Vollständigkeits-Check (referenzierte Beilagen vorhanden?)
- Konsistenz-Check (Widersprüche zwischen den Befehlen)
- Logik-Check (physische Machbarkeit: Kdt an 3 Orten gleichzeitig?)
- Informationslücken (was braucht meine Einheit, wo anfordern?)
- Sicherheitsrelevante Prüfungen (Bedrohungsstufen, ROE, Alarmorg)
**Output:** `00_dossier_check.md` mit Ampel-Bewertung (🔴/🟡/🟢)
**Status:** Template erstellt, noch nicht in INDEX.yaml gewired

### FR-002: Auftragsanalyse als fixes Produkt — P0
**Beschreibung:** Die BFE 5.4.1 Auftragsanalyse (fixe 4-Zeilen-Tabelle) muss IMMER produziert werden.
**Tabelle:** Bedeutung der Aufgabe | Erwartete Leistung | Handlungsspielraum | Unterstützung
**Spalten:** Aussagen | Erkenntnisse | Konsequenzen (Mittel, Räume, Zeit, Info — muss zeichenbar sein!)
**Status:** ✅ In role.md, analyse.md und CHEAT_SHEET.md verankert. Output: `15_auftragsanalyse.md`

### FR-003: Interaktive Optionen bei KDT ENTSCHEID — P1
**Beschreibung:** Claude soll bei jeder Entscheidung 2-3 konkrete Optionen (A, B, C) mit Empfehlung zeigen. Kdt sagt nur "A" oder "B mit Anpassung X".
**Status:** ✅ In rules.md verankert (mit Beispiel). Wird bei nächstem `project generate` automatisch im System Prompt sein.

### FR-004: DOCX Writer Rewrite — P1
**Beschreibung:** Der DOCX Writer ist zu simpel für den komplexen Markdown den Claude produziert. Braucht:
- Markdown Bold/Italic → DOCX Runs mit Bold/Italic
- HTML-Kommentare (`<!-- -->`) ausblenden oder als Hervorhebung
- Blockquotes → eingerückter Text oder spezieller Style
- Multi-Spalten-Tabellen (nicht nur 2-spaltig)
- Aufträge-Tabelle (Pt 3) als spezielle Nx2-Tabelle mit Einheit links + Bullets rechts
- Absatzabstände korrekt
- `---` als Section Break oder ignorieren
**Aufwand:** L (Opus, 4-6h)

### FR-005: PNG/Bilder in Claude Project Knowledge — P2
**Beschreibung:** WAP-Seiten und Karten als PNG in die Knowledge Files des Claude Projects aufnehmen. Claude kann Bilder lesen und die Terminplanung aus dem WAP direkt in die Analyse einfliessen lassen.
**Implementierung:** `--include-images` Flag auf `project generate`
**Status:** ✅ Done (Paket L)

### FR-006: Dossier als Input für Project Generate — P0
**Beschreibung:** `milanon project generate --input test_output/anon/` soll das anonymisierte Dossier automatisch in den `knowledge/` Ordner kopieren.
**Status:** ✅ Done (Paket L)

### FR-007: One-Shot Full 5+2 Prompt — P2
**Beschreibung:** Ein einziger Mega-Prompt der den gesamten 5+2-Prozess in einem Shot durchführt (ohne interaktive Schritte). Nützlich für Batch-Verarbeitung oder wenn der Kdt keine Zeit für interaktives Review hat.
**Trade-off:** Weniger Kdt-Kontrolle, aber schneller.

### FR-008: Vault-Export als ZIP — P2
**Beschreibung:** `milanon dossier assemble` sammelt alle Produkte (Befehle, Beilagen, EP) und erstellt ein nummeriertes ZIP-Dossier wie es der Bat Kdt erwartet.
**Struktur:** 000_Allg_Bf.docx, 100_Ei_Bf.docx, 200_Wachtdienst_Bf.docx, etc.

### FR-009: Starter Kit für andere Kdt — P3
**Beschreibung:** `milanon starter-kit export` erstellt ein PII-freies Paket mit Doktrin, Templates, Config das an andere Kdt im Bat verteilt werden kann. `milanon starter-kit import` importiert es.

### FR-010: Claude Desktop MCP Integration — P3
**Beschreibung:** Claude Desktop kann über MCP direkt auf das Filesystem zugreifen. MilAnon könnte als MCP-Server fungieren und Claude Desktop die Befehle direkt ausführen lassen (anonymize, pack, export) ohne Terminal.

### FR-011: Desktop App (Electron/Tauri) — P3
**Beschreibung:** Drag & Drop PDF → 5+2 durchklicken → DOCX raus. Kein Terminal nötig. Das Unicorn-Produkt.

### FR-012: Erkennung Strassennamen ohne Suffix — P2
**Beschreibung:** Adressen wie "Fesenacker 3", "Tumma 9", "Falken 3" werden nicht erkannt weil sie nicht auf "-strasse", "-weg" etc. enden. Pattern: `[A-Z][a-z]+\s+\d{1,3}` in der Nähe von Personendaten.

### FR-013: Erkennung Einzelnamen ohne Rang — P2
**Beschreibung:** Vor-/Nachnamen die ohne Rang-Prefix auftreten (z.B. in Adresslisten-Tabellen) werden nicht erkannt. Lösung: Kontext-basierte Erkennung — wenn in einer Tabelle mit AHV-Nr, Telefon, PLZ steht, sind Wörter in bestimmten Spalten sehr wahrscheinlich Namen.

---

## EPICS — Status nach E2E-Test

### Phase 1: Core Engine (v0.3.0) — ✅ DONE
520 Tests. Alle 13 CLI Commands. 5 GUI Pages.

### Phase 2: Doctrine + Workflows (v0.5.0) — ✅ CODE COMPLETE

| Epic | Status | Tests | Offene Bugs |
|---|---|---|---|
| E14: Doctrine KB | ✅ Done | 14 Extracts generiert | — |
| E15: 5+2 Workflows | ✅ Done (3 Workflows + Infra) | 672+ Tests | BUG-018 (Rich Output) |
| E16: Claude Project Generator | ✅ Done (Basis) | 5 Tests | BUG-014 bis BUG-017 (Paket L) |

### Phase 3: DOCX Pipeline (v0.7.0) — 🔧 PARTIAL

| Epic | Status | Offene Bugs |
|---|---|---|
| E17: DOCX Export | 🔧 Funktional aber nicht production-ready | BUG-005 bis BUG-011 (Writer Rewrite) |

### Phase 4: Quality + Polish (v0.8.0) — ❌ OPEN

| Feature | Prio | Status |
|---|---|---|
| FR-001: Dossier Quality Check | P0 | Template erstellt, nicht gewired |
| FR-004: DOCX Writer Rewrite | P1 | Mega-Prompt nötig |
| FR-012: Strassennamen-Erkennung | P2 | Open |
| FR-013: Einzelnamen-Erkennung | P2 | Open |
| GUI Overhaul | P1 | 🔧 Paket G läuft |

### Phase 5: Distribution (v1.0) — ❌ OPEN

| Feature | Prio | Status |
|---|---|---|
| FR-008: Dossier Assembly ZIP | P2 | Open |
| FR-009: Starter Kit | P3 | Open |
| FR-010: MCP Integration | P3 | Open |
| FR-011: Desktop App | P3 | Open |

---

## ERKENNTNISSE AUS E2E-TEST (25.03.2026)

### Der Einsatzbefehl war nicht wirklich ein WK-Befehl
Claude hat einen Ei Bf für die Kp Übungen "DIFESA" und "ATTACO" geschrieben — das ist ein Ausbildungsbefehl für eine spezifische Übung, kein WK-Gesamtbefehl. Was der Kdt tatsächlich braucht ist ein **Kp-Dossier** mit mehreren Befehlen:

| Dok | Befehl | Wann | Status |
|---|---|---|
| 000 | Allgemeiner Befehl (Dienstbetrieb, Ordnung, Sicherheit) | Vor Einrücken | Template vorhanden, nicht getestet |
| 100 | Befehl Ausbildung KVK | KVK-Woche | Fehlt als Workflow |
| 200 | Befehl Erstausbildung Trp | Wo 1 | Fehlt als Workflow |
| 300 | Wachtdienstbefehl | Permanent | Template vorhanden, nicht getestet |
| 500 | Ei Bf Kp Ü "DIFESA" (Vtg) | Wo 2 | Getestet — Output war OK aber gemischt mit "ATTACO" |
| 501 | Ei Bf Kp Ü "ATTACO" (Ag) | Wo 2-3 | Fehlt als separater Befehl |
| EP1 | EP Halten Standort | Permanent | Fehlt als Workflow |
| EP2 | EP Kampf Interessenraum | Permanent | Fehlt als Workflow |

**Erkenntnis:** Der Workflow `ei-bf` muss klärer spezifizieren WELCHER Befehl geschrieben wird. Der Prompt muss den Kdt fragen: "Welchen Befehl willst du jetzt schreiben?" statt einfach "den Einsatzbefehl".

**TODO:** Layer 4 Template `ei-bf.md` überarbeiten — Optionen anbieten (Allg Bf, Ausb Bf KVK, Erstausb, Kp Ü Vtg, Kp Ü Ag) oder als separate Workflows aufteilen.

---

## NÄCHSTE SCHRITTE (Prioritätsreihenfolge)

1. ✅ **Paket L mergen** (Project Generator Fix) — Done
2. **Paket G mergen** (GUI Overhaul) — Branch ready
3. **Alle Feature-Branches mergen** → main, `git tag v0.5.0`, `git push --tags`
4. **FR-001 in INDEX.yaml wiren** (Dossier Check Workflow) — Template vorhanden
5. **FR-004: DOCX Writer Rewrite** (Opus Mega-Prompt, ~4h)
6. **Manueller Test mit echtem Bat Dossier als Claude Project** (31.03)
