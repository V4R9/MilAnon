# MilAnon — User Journey: WK 2026

> Praktischer Walkthrough: Was passiert ab dem 31.03.2026 Schritt für Schritt?
> Perspektive: Kp Kdt Inf Kp 56/1, erster WK als Einheitskommandant
> Ziel: User Stories und Gaps identifizieren für Roadmap

---

## WICHTIG: Paradigmenwechsel 2026 — Berrm statt klassischer WK

Die Ter Div / Inf Bat 56 plant den WK 2026 NICHT als klassischen Ausbildungsdienst (ADF), sondern als **Bereitschaftsraum (Berrm)** — Einsatzverfahren B.02 gemäss 53.005.21.

Das ändert fundamental:
- **Grundbefehl** = Ei Bf Berrm (5-Punkte-Befehl), NICHT Bf Dienstbetrieb
- **Taktischer Rahmen** = permanent (ganzer Dienst), nicht nur Übungsanlage
- **Zeitstruktur** = Dienstrad (Einsatz/Reserve/Ruhe), nicht Wochenarbeitsplan
- **Ausbildung** = Mittel zum Zweck, nicht Hauptzweck
- **Sicherung** = taktisch mit Checkpoints und Interessenraum, nicht nur Unterkunft
- **3 Phasen**: Bezug + Erstellen Ei-Bereitschaft → Erhalten → Raumerweiterung
- **2 Eventualplanungen**: EP Halten Standort + EP Kampf Interessenraum
- **ZMZ** = operativ (Zivilbevölkerung ist taktischer Faktor)

Konsequenz für MilAnon: Der 5+2 wird WICHTIGER, nicht weniger relevant. Im Berrm ist die AP echt — nicht nur für die Übungsanlage. Aber die Skeletons und Workflows müssen angepasst werden.

Siehe: [Paradigmenwechsel_WK_zu_Berrm.md](../data/doctrine/Paradigmenwechsel_WK_zu_Berrm.md)

---

## Ausgangslage am 31.03.2026

### Was du HAST:

**Auf dem Mac:**
- MilAnon v0.3.0 installiert (CLI + GUI)
- Obsidian Vault: `~/Sandro Personal Vault/10_Projects/WK 2026/`
  - `Personelles/` — 12 Personen-Dossiers + Dashboard (von MilAnon erstellt)
- MilAnon DB: 1115 Entities (PISA + Bat Stab importiert)

**Auf SharePoint (milweb.ch → OneDrive sync):**
- `OneDrive-Armee2030/Inf Kp 56_1/WK 2026/`
  - `Personelles Mails/` — 21 EML Mails (KVK, TDL, Admin Entlassungen)

**In deinem Kopf:**
- BFE 52.080 + 52.081 gelesen (theoretisch)
- Aber: Noch nie praktisch angewendet
- Kein Vorjahres-Dossier für DEINE Kp (aber Zugriff auf alte Dossiers anderer Kp)

### Was du BEKOMMST am 31.03:

Der Bat Kdt schickt dir das **Befehlsdossier WK 2026 Inf Bat 56**. Das kommt als:
- 1 PDF (60-80 Seiten) ODER mehrere DOCX-Dateien
- Per Mail oder auf dem SharePoint
- Enthält: Bat Befehl + alle Beilagen (WAP/Picasso, Karten, Telefonliste, etc.)

---

## SCHRITT 1: Dossier empfangen und sichern (Tag 1, 31.03)

### Was du tust:
1. Mail/SharePoint öffnen → Bat Dossier herunterladen
2. Speichern nach: `OneDrive-Armee2030/Inf Kp 56_1/WK 2026/Bat Dossier/`

### Was du brauchst von MilAnon: NICHTS
Das ist reine Dateiablage. Aber die Ordnerstruktur sollte MilAnon kennen.

### 💡 GAP: Projekt-Initialisierung
**Heute:** Du musst manuell wissen welche Ordner du brauchst.
**Ideal:** `milanon init --unit "Inf Kp 56/1" --wk 2026` erstellt die komplette Ordnerstruktur:
```
WK_2026_Inf_Kp_56_1/
  01_Input/
    Bat_Dossier/          ← hier kommt das PDF rein
    Personelles_Mails/    ← hier kommen neue Mails rein
    PISA/                 ← CSV Exports
  02_Anonymized/          ← MilAnon Output
  03_Claude_Workspace/    ← Pack/Unpack Zwischenspeicher
  04_Vault/               ← Obsidian Vault (oder Symlink)
    Personelles/          ← besteht bereits
    Dossier/              ← Kp Befehlsdossier
    Planung/              ← WAP, Ausb, Logistik
    Einsatz/              ← Einsatzbefehle
  05_Export/              ← DOCX/PDF für Distribution
```

**User Story:** *Als Kp Kdt will ich mit einem Befehl meine komplette WK-Projektstruktur initialisieren, damit ich von Anfang an organisiert bin und MilAnon weiss wo alles liegt.*

---

## SCHRITT 2: Bat Dossier anonymisieren (Tag 1, 31.03, Abend)

### Was du tust:
```bash
# DB ist schon initialisiert von den Personelles-Mails
milanon anonymize "01_Input/Bat_Dossier/" --output "02_Anonymized/bat_dossier/" \
  --recursive --embed-images
```

### Was passiert:
- MilAnon parsed das PDF (60-80 Seiten)
- Erkennt Namen, AHV, Telefon, Adressen, Einheiten
- WAP/Picasso-Seiten → als PNG eingebettet
- Output: `02_Anonymized/bat_dossier/WK25_InfBat56_Bf_Dossier_56.md`

### Was du prüfst:
```bash
milanon review "02_Anonymized/bat_dossier/" --dry-run
```
→ Zeigt: "15 Kandidaten gefunden: HALTER, SUTER, MEIER..."
→ Das sind Namen aus dem Bat Stab die nicht in deiner PISA waren.

```bash
milanon review "02_Anonymized/bat_dossier/" --auto-add
```
→ "15 Namen zur DB hinzugefügt. Nächster Lauf fängt sie."

```bash
# Re-anonymize mit den neuen Namen
milanon anonymize "01_Input/Bat_Dossier/" --output "02_Anonymized/bat_dossier/" \
  --recursive --embed-images --force
```

### Was funktioniert HEUTE: ✅
- Anonymisierung funktioniert
- Review Loop funktioniert
- Embed Images funktioniert

### 💡 GAP: Re-Run nach Review
**Heute:** Du musst manuell --force und den gleichen Befehl nochmal tippen.
**Ideal:** `milanon review --auto-add --re-run` → macht beides in einem Schritt.

**User Story:** *Als Kp Kdt will ich nach dem Review automatisch re-anonymisieren, damit ich nicht zwei Befehle tippen muss.*

---

## SCHRITT 3: Dossier verstehen — Initialisierung + Problemerfassung (Tag 1-2)

### Was du tust:
Das ist der WICHTIGSTE Schritt. Du musst das 70-Seiten-Dossier verstehen.

```bash
milanon context --unit "Inf Kp 56/1" --output "02_Anonymized/bat_dossier/CONTEXT.md"
```

Dann:
```bash
milanon pack --workflow analyse --input "02_Anonymized/bat_dossier/" \
  --unit "Inf Kp 56/1"
```

### Was in der Zwischenablage landet (= was du in Claude.ai pastest):

```markdown
[SYSTEM: Du bist der Stabsassistent eines Schweizer Kp Kdt...]
[CONTEXT: Inf Kp 56/1, unter Inf Bat 56, Ter Div 2...]
[AUFGABE: Initialisierung + Problemerfassung nach BFE 52.080 Kap 5.1]
[DOKTRIN: BFE Kap 5.1.1 Initialisierung — 4-Farben-Markierung...]

--- ANONYMISIERTES BAT DOSSIER ---
[Das ganze Dossier als Markdown, 20'000-40'000 Zeichen]
```

### Was Claude liefert:

**4-Farben-Extraktion:**
```
# BLAU — Was betrifft [EINHEIT_001] direkt
- Auftrag: "Stellt die Mobilisierung mittels Mob U sicher..."
- Phase 2: "Unterstützt das GWK im Sektor..."
- ...

# GRÜN — Direkt übernehmen in Kp Bf
- Deckname: "COMPENDIO"
- Kartenmassstab: LK 1:50'000
- Nachbartruppen: [EINHEIT_008] sperrt den Raum...
- ...

# ROT — Bedrohung
- Bestimmende Lageentwicklungsmöglichkeit: ...
- Weitere: ...

# GELB — Besondere Anordnungen
- ROE/ROB: gem Taschenkarte A & C
- TOZZA
- ...
```

**Problemerfassungs-Matrix:**
```
| Teilproblem | Aufgaben | Handlungsrichtlinien | Produkte | Prio | Wer |
|---|---|---|---|---|---|
| TP1: Mob/Einrücken | ... | ... | Vs Bf | 2 | Kdt Stv |
| TP2: KVK | ... | ... | Bf Ausbildung | 2 | Kdt |
| TP3: Einsatz GWK | ... | ... | Ei Bf | 1 | Kdt |
| TP4: WEMA | ... | ... | Wema Konzept | 3 | Einh Fw |
```

**SOMA-Liste:**
```
| Sofort | Was | Wer |
|---|---|---|
| O | Kdt Stv über Auftrag orientieren | Kdt |
| E | Erkundung Standort bestellen | Kdt Stv |
| V | Kontakt Nachbar-Kp aufnehmen | Kdt |
| V | Mat-Bestellung bei S4 | Einh Fw |
```

**Synchronisationsmatrix** (Zeitplan)

### Was du dann tust:
```bash
# Claude's Output kopieren
milanon unpack --clipboard --output "04_Vault/Planung/" --split
```

### Was funktioniert HEUTE: ⚠️ Teilweise
- ✅ `milanon context` funktioniert
- ✅ `milanon pack --template analyse` funktioniert (generisches Template)
- ❌ `milanon pack --workflow analyse` existiert NICHT (kein --workflow Flag)
- ❌ Kein 4-Farben-System Prompt
- ❌ Kein Doktrin-Auszug (BFE Kap 5.1) im Prompt
- ❌ Kein Problemerfassungs-Matrix Template
- ✅ `milanon unpack --clipboard --split` funktioniert

### 💡 GAPS:

**GAP A: --workflow Flag**
Heute gibt es nur `--template`. Wir brauchen `--workflow` das automatisch:
1. Den richtigen System Prompt lädt (Layer 1+2+5)
2. Den richtigen Doktrin-Auszug inkludiert (Layer 3)
3. Die richtige Aufgabe formuliert (Layer 4)
4. Den richtigen Skeleton mitliefert

**User Story:** *Als Kp Kdt will ich `milanon pack --workflow analyse` ausführen und das Tool baut mir automatisch den kompletten Prompt inkl. Doktrin-Auszug und strukturierter Aufgabenstellung zusammen.*

**GAP B: Chapter Extraction**
Die Doktrin-Dateien sind 280-669 KB gross. Claude's Kontext ist limitiert. Wir brauchen Extrakte.

**User Story:** *Als Kp Kdt will ich dass nur die relevanten Reglement-Kapitel im Prompt landen (z.B. BFE Kap 5.1 für Analyse, nicht das ganze BFE), damit der Prompt effizient ist und Claude's Kontext nicht verschwendet wird.*

**GAP C: 5-Layer System Prompt**
Heute ist der System Prompt ein einfaches Template. Wir brauchen die 5-Layer-Architektur.

**User Story:** *Als Kp Kdt will ich dass der System Prompt automatisch meine Einheit, die relevante Doktrin und die aktuelle Aufgabe enthält, damit Claude wie ein echter Stabsassistent arbeitet.*

---

## SCHRITT 4: BdL durchführen — AUGEZ Analyse (Tag 2-3)

### Was du tust:
Du reviewst die Analyse aus Schritt 3 in Obsidian. Dann:

```bash
milanon pack --workflow bdl --input "02_Anonymized/bat_dossier/" \
  --unit "Inf Kp 56/1" \
  --context "04_Vault/Planung/01_problemerfassung.md"
```

WICHTIG: Der BdL-Prompt braucht die Problemerfassung aus Schritt 3 als Input! Claude muss wissen was in Schritt 1 rauskam.

### Was Claude liefert:
- AUGEZ-Analyse (Faktor für Faktor mit AEK)
- Schlüsselbereiche ROT + BLAU
- Konsequenzen ROT → BLAU
- Bedrohungsbild (bestimmende + weitere Lageentwicklungsmöglichkeiten)

### Was du dann tust:
```bash
milanon unpack --clipboard --output "04_Vault/Planung/" --split
```

### 💡 GAP: Schrittverkettung
**Heute:** Jeder Schritt ist isoliert. Claude weiss nicht was in Schritt 1 rauskam.
**Ideal:** `--context` Flag das Vault-Dateien aus dem vorherigen Schritt mitschickt.

**User Story:** *Als Kp Kdt will ich beim Pack die Ergebnisse vorheriger Schritte als Kontext mitgeben können (`--context vault/Planung/`), damit Claude auf meinen bisherigen Produkten aufbaut statt bei null zu starten.*

---

## SCHRITT 5: Entschluss fassen — Varianten + Absicht (Tag 3-4)

### Was du tust:
```bash
milanon pack --workflow entschluss --input "02_Anonymized/bat_dossier/" \
  --unit "Inf Kp 56/1" \
  --context "04_Vault/Planung/"
```

### Was Claude liefert:
- 2-3 Varianten (mit ROS-Unterscheidung)
- Prüfung nach Einsatzgrundsätzen
- Empfehlung
- Entwurf Absicht + Aufträge

### Was DU tust (das kann Claude NICHT):
Du liest die Varianten und entscheidest. Du formulierst DEINE Absicht.
Du trägst das in Obsidian ein: `04_Vault/Planung/32_entschluss.md`

Das ist der **<!-- KDT ENTSCHEID -->** Moment.

### 💡 GAP: KDT ENTSCHEID Workflow
**Heute:** Claude liefert Text, du editierst in Obsidian, aber es gibt keinen formalen "Entscheid bestätigt" Mechanismus.
**Ideal:** In der GUI: Ein "Entscheid bestätigen" Button der den Status trackt und den nächsten Schritt freischaltet.

**User Story:** *Als Kp Kdt will ich meine Entscheide formal bestätigen können (z.B. "Absicht bestätigt"), damit das Tool weiss dass es mit dem nächsten Schritt weitergehen kann und damit ich einen Audit Trail habe.*

---

## SCHRITT 6: Kp Befehl schreiben (Tag 4-5)

### Was du tust:
```bash
milanon pack --workflow kp-befehl --input "02_Anonymized/bat_dossier/" \
  --unit "Inf Kp 56/1" \
  --context "04_Vault/Planung/"
```

### Was Claude liefert:
Den kompletten 5-Punkte-Befehl (Dok 000) basierend auf:
- Schritt 3: Initialisierung (GRÜN-Textbausteine direkt übernommen)
- Schritt 4: BdL (Bedrohung für Punkt 1)
- Schritt 5: Entschluss (Absicht + Aufträge für Punkt 2+3)
- Skeleton: `000_allgemeiner_befehl.md` als Strukturvorlage

### Was du dann tust:
```bash
milanon unpack --clipboard --output "04_Vault/Dossier/" --split
```

Dann in Obsidian: Review, Anpassungen, deine persönliche Note.

### Dann Export:
```bash
milanon export "04_Vault/Dossier/000_Allgemeiner_Befehl.md" \
  --format docx --template armee-befehl
```

### Was funktioniert HEUTE: ❌ Wenig
- ✅ `milanon unpack --clipboard --split` funktioniert
- ❌ `milanon pack --workflow kp-befehl` existiert nicht
- ❌ `milanon export --format docx` existiert nicht (E17)
- ❌ Keine Skeleton-Integration im Pack

### 💡 GAPS:

**GAP: DOCX Export**
Der Kp Befehl muss als DOCX raus — zum Drucken, Verteilen, dem Bat Kdt zeigen.

**User Story:** *Als Kp Kdt will ich meinen fertigen Befehl als DOCX mit Armee-Formatierung exportieren können (Kopfzeile mit Grad+Name, Seitennummern, korrekte Gliederung), damit ich ihn direkt ausdrucken und verteilen kann.*

---

## SCHRITT 7: Wachtdienstbefehl (Tag 5-6)

### Was du tust:
```bash
milanon pack --workflow wachtdienst --input "02_Anonymized/bat_dossier/" \
  --unit "Inf Kp 56/1" \
  --context "04_Vault/Dossier/000_Allgemeiner_Befehl.md"
```

### Was Claude liefert:
Kompletter Wachtdienstbefehl nach WAT 51.301 Struktur, basierend auf:
- Bat Sicherheitsbefehl (aus Dossier)
- Standort-Info (aus Dossier)
- Skeleton: `300_wachtdienstbefehl.md`
- Doktrin: WAT-Auszug

### Was gleich funktioniert wie in Schritt 6.

---

## SCHRITT 8: Weitere Dokumente (Tag 6-10)

Gleicher Flow für:
- 100 Bf Dienstbetrieb (`--workflow dienstbetrieb`)
- 200 Bf Ausbildung (`--workflow ausbildung`)
- 500 Einsatzbefehl (`--workflow einsatzbefehl`)
- Beilagen (Telefonliste, Terminliste, Notfall-Alarmierung)

---

## SCHRITT 9: Dossier zusammenstellen + Befehlsausgabe vorbereiten (Tag 10-14)

### Was du tust:
Das ganze Dossier zusammenstellen. Nummerierung prüfen. Beilagen vollständig.

```bash
milanon export "04_Vault/Dossier/" --format docx --all --numbering auto
```

### 💡 GAP: Dossier-Assembly
**Heute:** Du musst jedes Dokument einzeln exportieren und manuell nummerieren.
**Ideal:** `milanon dossier assemble` liest alle Dokumente im Vault, nummeriert sie gemäss der Standard-Struktur (000, 001, 100, 200, 300, 500) und produziert ein zusammenhängendes DOCX oder eine ZIP mit allen Einzeldokumenten.

**User Story:** *Als Kp Kdt will ich mein ganzes Dossier mit einem Befehl als nummeriertes, korrekt gegliedertes Dokumentenpaket exportieren, damit ich es als Ganzes an die Truppe verteilen kann.*

---

## SCHRITT 10: Neue Mails während WK-Vorbereitung (laufend)

### Was passiert:
Zwischen dem 31.03 und dem Einrücken (08.06) kommen neue Mails rein:
- Weitere TDL-Gesuche
- Antworten auf deine Anfragen
- Bat-Updates, Änderungen

### Was du tust:
```bash
# Neue Mails in den Input-Ordner legen
# Dann Round-Trip:
milanon anonymize "01_Input/Personelles_Mails/" --output "02_Anonymized/mails/" --recursive
milanon anonymize "04_Vault/Personelles/" --output "02_Anonymized/vault_personelles/"
milanon pack --template update-dashboard \
  --input "02_Anonymized/" --unit "Inf Kp 56/1"
# → Claude: "Hier sind 3 neue Mails + aktueller Vault-Stand. Update."
milanon unpack --clipboard --output "04_Vault/Personelles/" --in-place
```

### Was funktioniert HEUTE: ✅ Komplett
Das ist der Round-Trip der schon gebaut ist!

---

## SCHRITT 11: Rapport-Vorbereitung + Dispo-Begehung (T-2 Wochen)

### Was du tust:
Der Bat Kdt will eine Dispo-Begehung. Du musst zeigen: Problemerfassung, BdL, Varianten, Entschluss.

```bash
milanon pack --workflow rapport --input "04_Vault/Planung/" \
  --unit "Inf Kp 56/1"
```

### Was Claude liefert:
- Zusammenfassung aller Planungsprodukte
- Offene Punkte / Fragen an den Bat Kdt
- Kp-Stand (Personal, Material, Ausbildung)

### 💡 GAP: Rapport-Template
**User Story:** *Als Kp Kdt will ich mit einem Befehl eine Rapport-Vorbereitung generieren die alle meine bisherigen Planungsprodukte zusammenfasst, damit ich mich auf die Dispo-Begehung vorbereite.*

---

## SCHRITT 12: WK läuft — tägliche Operationen (3 Wochen)

### Was du tust täglich:
- Morgens: Neue Mails verarbeiten (Round-Trip)
- Abends: Rapport vorbereiten, Pendenzen updaten
- Laufend: Personalfälle bearbeiten (Gesuche beantworten)

```bash
# Täglicher Update-Zyklus:
milanon anonymize "01_Input/neue_mails_heute/" --output "02_Anonymized/heute/"
milanon pack --template update-dashboard --input "02_Anonymized/heute/"
milanon unpack --clipboard --output "04_Vault/Personelles/" --in-place
```

### 💡 GAP: Täglicher Quick-Workflow
**Heute:** 3 Befehle für ein tägliches Update.
**Ideal:** `milanon daily-update --input neue_mails/ --vault Vault/Personelles/` → alles in einem Schritt.

**User Story:** *Als Kp Kdt will ich neue Mails mit einem einzigen Befehl verarbeiten und in meinen Vault integrieren, damit ich den täglichen Update in 5 Minuten statt 15 erledigen kann.*

---

## SCHRITT 13: WK fertig — Übergabe (T+3 Wochen)

### Was du tust:
```bash
milanon starter-kit export --unit "Inf Kp 56/1" --output "WK2026_kit.zip"
```

### Was im Kit ist:
- Doctrine files (Reglemente als .md)
- Templates (alle Workflow-Templates)
- Skeletons (Dokumentvorlagen)
- Claude Project Setup (System Prompt + Knowledge)
- KEIN Mapping-DB (PII bleibt lokal)

Dein Nachfolger: `milanon starter-kit import WK2026_kit.zip` → sofort ready.

---

## Zusammenfassung: Was gibt es, was fehlt?

### ✅ Funktioniert heute (v0.3.0):
- Anonymisierung (PDF, EML, DOCX, XLSX)
- Review Loop (unbekannte Namen lernen)
- Pack mit Templates (6 Templates)
- Unpack (Clipboard, Split, In-Place)
- Round-Trip (Re-anonymize → Update → De-anonymize)
- Context Generator (Einheits-Hierarchie)
- Obsidian Integration (Wiki-Links, Filenames)
- CLI (13 Commands) + GUI (5 Pages)

### ❌ Fehlt für den 31.03-Workflow:

#### Kern-Infrastruktur (für ALLE Workflows):
| Gap | Epic | Priority | Beschreibung |
|---|---|---|---|
| `--workflow` Flag | E15 | **P0** | Pack baut Prompt aus 5 Layers + Doktrin + Skeleton |
| Chapter Extraction | E14 | **P0** | Doktrin-Kapitel extrahieren für Token-effiziente Prompts |
| 5-Layer System Prompt | E15 | **P0** | Rolle + Kontext + Doktrin + Aufgabe + Regeln |
| `--context` Flag | E15 | **P0** | Vorherige Vault-Produkte als Input mitgeben |
| ADF/Berrm Modus-Flag | E15 | **P0** | `--mode berrm` oder `--mode adf` — wählt Skeleton + Doktrin |

#### Workflows (5+2 Schritte):
| Gap | Epic | Priority | Beschreibung |
|---|---|---|---|
| Workflow: Analyse | E15 | **P0** | 4-Farben + Problemerfassung + SOMA + Zeitplan |
| Workflow: BdL | E15 | **P1** | AUGEZ + AEK + Konsequenzen (Berrm: ZMZ + Zivilbev als Faktor) |
| Workflow: Entschluss | E15 | **P1** | Varianten + Prüfung + Absicht (Berrm: inkl. Dienstrad-Konzept) |
| Workflow: Ei-Bf-Berrm | E15 | **P0** | 5-Punkte-Befehl Berrm mit 3-Phasen-Absicht + Dienstrad |
| Workflow: Wachtdienst | E15 | **P0** | WAT-konformer Wachtdienstbefehl (Berrm: taktische Sicherung) |
| Workflow: EP Halten | E15 | **P1** | Eventualplanung Halten Standort |
| Workflow: EP Interessenraum | E15 | **P1** | Eventualplanung Kampf im Interessenraum (Verzögerung) |

#### Berrm-spezifisch:
| Gap | Epic | Priority | Beschreibung |
|---|---|---|---|
| Berrm-Skeleton | E15 | **P0** | ✅ DONE — `500_einsatzbefehl_berrm.md` erstellt |
| Dienstrad-Rechner | E15 | **P2** | Dreier-/Vierergliederung, Ablöserhythmus berechnen |
| EP Templates | E15 | **P1** | Skeleton für EP Halten + EP Kampf Interessenraum |
| Paradigmenwechsel-Dok | E14 | **P0** | ✅ DONE — In Project Knowledge + data/doctrine/ |

#### Output + Distribution:
| Gap | Epic | Priority | Beschreibung |
|---|---|---|---|
| DOCX Export | E17 | **P1** | Armee-formatierter Export |
| Dossier Assembly | E17 | **P2** | Ganzes Dossier nummeriert exportieren |

#### Nice-to-have:
| Gap | Epic | Priority | Beschreibung |
|---|---|---|---|
| `milanon init` | NEW | **P2** | Projektstruktur initialisieren |
| Review --re-run | E2 | **P2** | Review + Re-Anonymize in einem Schritt |
| `milanon daily-update` | E10 | **P2** | Täglicher Ein-Befehl-Update |
| Starter Kit Export | E18 | **P3** | Für Nachfolger exportieren |
| Claude Project Gen | E16 | **P3** | Claude Project für andere Kdt |

### Die kritische Frage: Was muss bis 31.03 stehen?

**MUSS (für Tag 1-2 — Bat Dossier verstehen):**
1. Chapter Extraction (E14) — sonst sind die Prompts zu lang
2. `--workflow analyse` (E15) — 4-Farben + Problemerfassung
3. 5-Layer System Prompt — sonst ist Claude nicht doktrinkonform
4. `--context` Flag — sonst kann Claude nicht auf vorherige Schritte aufbauen
5. `--mode berrm` Flag — Modus-Wahl bestimmt Skeleton + Doktrin-Auszüge

**SOLLTE (für Woche 1-2 — Ei Bf Berrm schreiben):**
6. `--workflow ei-bf-berrm` — DAS Hauptprodukt (Grundbefehl im Berrm-Modus)
7. `--workflow wachtdienst` — jetzt Teil der taktischen Sicherung
8. EP-Templates (Halten + Interessenraum) — Berrm-Pflicht
9. DOCX Export — für die Distribution

**KANN WARTEN (bis WK):**
10. Erg Bf Dienstbetrieb
11. Erg Bf Ausbildung
12. Dienstrad-Rechner
13. Daily Update Shortcut
14. Dossier Assembly
15. Starter Kit

### Berrm-Impact auf das Produkt: Zusammenfassung

Der Paradigmenwechsel ist POSITIV für MilAnon:

| Aspekt | Warum positiv |
|---|---|
| **5+2 wird wichtiger** | Im Berrm ist die AP echt (für den realen Raum), nicht nur für Übungsanlage |
| **Ei Bf = Grundbefehl** | Unser Einsatzbefehl-Skeleton wird zum Hauptprodukt, nicht nur zur Übung |
| **BFE Teil 1 zentral** | Genau das Reglement das wir am tiefsten integriert haben |
| **Doktrin-Tiefe zahlt sich aus** | Berrm erfordert echte AUGEZ, echte Varianten, echte EP — genau was der 5+2-Assistent liefert |
| **Differenzierung vs ChatGPT** | Ein generischer LLM kennt Einsatzverfahren B.02 nicht — MilAnon schon |

Der einzige neue Aufwand:
- 1 neues Skeleton: `500_einsatzbefehl_berrm.md` (✅ erstellt)
- Modus-Flag: `--mode berrm` vs `--mode adf`
- Berrm-spezifische Prompt-Anpassungen (ZMZ, Dienstrad, 3 Phasen, EP)
