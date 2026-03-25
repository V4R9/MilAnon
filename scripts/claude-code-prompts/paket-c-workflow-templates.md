# MEGA-PROMPT: Paket C — Workflow Task Templates (Layer 4)

## Context
Read CLAUDE.md. You're creating CONTENT files (Markdown templates), not code.
Read `docs/PRODUCT_DESIGN_COMMAND_ASSISTANT.md` for full 5+2 process details.
Read `docs/PRODUCT_DESIGN_TF17_APPENDIX.md` for tactical vocabulary.
Read `data/doctrine/skeletons/5_punkte_befehl_universal.md` for the skeleton structure.

## Branch
```bash
git checkout -b feat/e15-workflow-templates
```

## Create these files

### 1. `data/templates/workflows/analyse.md`

This is the Layer 4 task template for the FIRST step of the 5+2: Initialisierung + Problemerfassung.

Content (in GERMAN — per D-003):
```
# Aufgabe: Initialisierung und Problemerfassung (BFE 52.080 Kap 5.1)

Du erhältst den anonymisierten Einsatzbefehl des Truppenkörpers (Bat Bf).
Führe die Initialisierung und Problemerfassung gemäss BFE Kap 5.1 durch.

## Schritt 1: 4-Farben-Initialisierung (BFE 5.1.1)

Markiere den Bat Bf mit den 4 Farben:
- **BLAU**: Teile der Absicht und des Auftrags die {user_unit} direkt betreffen
- **GRÜN**: Passagen die direkt in den Kp Bf übernommen werden können (Nachbartruppen, Textbausteine)
- **ROT**: Bedrohungsrelevante Passagen inkl. Eventualplanungen
- **GELB**: Besondere Anordnungen die {user_unit} betreffen

Produziere 4 separate Abschnitte mit den extrahierten Passagen.

## Schritt 2: Problemerfassung (BFE 5.1.2)

### Problementdeckung
- Was ist der IST-Zustand?
- Was ist der SOLL-Zustand?
- Visualisiere das Gesamtproblem entlang einer Zeitachse

### Problemklärung — Zerlegung in Teilprobleme
Erstelle eine Problemerfassungs-Matrix als Markdown-Tabelle:

| Teilproblem | Aufgabenumschreibung | Handlungsrichtlinien | Produkte | Prio | Wer |
|---|---|---|---|---|---|

Typische Teilprobleme: Mobilisierung/Einrücken, KVK, Einsatz, WEMA
<!-- BERRM: Typische Teilprobleme: Bezug Berrm, Erstellen Ei-Bereitschaft, Kampfvorbereitung, Raumerweiterung, Dienstbetrieb, Ausbildung -->
<!-- ADF: Typische Teilprobleme: Einrücken/AGA-Rep, Verbandsausbildung, Verbandsübung/Einsatz, WEMA -->

### Problembeurteilung
Priorisiere nach Eisenhower-Prinzip (wichtig/dringend).
Weise Erledigungsinstanzen zu (Kdt, Kdt Stv, Einh Fw, Zfhr).

## Schritt 3: Sofortmassnahmen (BFE 5.2)

Identifiziere SOMA nach OEBAS-VIV:
| Wann | SOMA | Wer |
|---|---|---|
| Sofort | O — Orientierung: ... | |
| Sofort | E — Erkundung: ... | |
| ... | ... | ... |

Erstelle auch eine Pendenzen-Liste mit Terminen.

## Schritt 4: Zeitplanung (BFE 5.3)

Erstelle eine Synchronisationsmatrix:
- Interner Zeitplan (eigene AP)
- Externer Zeitplan (Bat-Vorgaben, Unterstellte)
- Viertelregel anwenden: ¼ eigene Planung, ¾ für Unterstellte

## Output-Format

Produziere folgende Dateien (jeweils mit # Dateiname als Header, getrennt durch ---):

1. `01_blau_eigener_auftrag.md`
2. `02_gruen_textbausteine.md`
3. `03_rot_bedrohung.md`
4. `04_gelb_beso_anordnungen.md`
5. `10_problemerfassung.md`
6. `12_sofortmassnahmen.md`
7. `13_pendenzen.md`
8. `14_synchronisationsmatrix.md`
```

### 2. `data/templates/workflows/ei-bf.md`

Layer 4 for step 5: Befehlsgebung. References the universal skeleton.

Content:
```
# Aufgabe: Einsatzbefehl Einheit (BFE 52.080 Kap 5.7)

Erstelle den vollständigen Einsatzbefehl für {user_unit} als 5-Punkte-Befehl.

Verwende die Struktur aus dem beigefügten Skeleton.
Fülle jeden Punkt basierend auf den bisherigen Planungsprodukten (im Kontext mitgeliefert).

## Zusammensetzung (BFE 52.080 Kap 5.7.1):

Punkt 1 — Orientierung: 
- 1.1 Bedrohung: Aus der BdL (Datei 24_bedrohung.md oder aus Bat Bf)
- 1.2 Erhaltener Auftrag: Aus der Initialisierung (01_blau_eigener_auftrag.md)
- 1.3 Nachbartruppen: Aus der Initialisierung (02_gruen_textbausteine.md)

Punkt 2 — Absicht:
- Aus dem Entschluss (33_absicht_auftraege.md)
- Formuliere mit taktischen Aufgaben (sperren, halten, bewachen, vernichten, etc.)
<!-- BERRM: Absicht MUSS die 3 Phasen des Berrm abdecken -->
<!-- ADF: Absicht deckt die WK-Phasen ab -->

Punkt 3 — Aufträge:
- Aus dem Entschluss
- Tabellenformat: | Element | Auftrag |
- Auftragstaktik: WAS, nicht WIE
<!-- BERRM: Aufträge orientieren sich am Dienstrad (Einsatz/Reserve/Ruhe) -->

Punkt 4 — Besondere Anordnungen:
- Aus der Planentwicklung und dem Bat Bf
<!-- BERRM: ZMZ, ROE/ROB, Dienstrad, 2 Eventualplanungen prominent -->

Punkt 5 — Standorte:
- KP, Zugsräume, Log-Einrichtungen

Beilagen + Verteiler gemäss Skeleton.

## Markierungen
- Verwende <!-- KDT ENTSCHEID: ... --> wo der Kommandant persönlich entscheiden muss
- Verwende <!-- FILL: ... --> wo Informationen aus dem Bat Bf oder der Erkundung fehlen

## Output: EIN zusammenhängendes Dokument `50_einsatzbefehl_einheit.md`
```

### 3. `data/templates/workflows/wachtdienst.md`

Layer 4 for Wachtdienstbefehl (standalone workflow, covers full 5+2 cycle for Sicherung).

Content: Similar structure but references WAT 51.301 skeleton (`data/doctrine/skeletons/300_wachtdienstbefehl.md`). Include the full 10-point WAT structure. Mark Berrm-specific content (taktische Sicherung mit Checkpoints, Interessenraum-Überwachung) vs ADF (reiner Unterkunftsschutz).

## Files you MUST NOT touch
- ALL Python source code (src/)
- ALL test files (tests/)
- `data/templates/role.md` (Paket D creates this)
- `data/templates/rules.md` (Paket D creates this)

## Commit
```bash
git add -A
git commit -m "feat(e15): workflow task templates for analyse, ei-bf, wachtdienst

- analyse.md: 4-Farben + Problemerfassung + SOMA + Zeitplan (Layer 4)
- ei-bf.md: 5-Punkte-Befehl assembly instructions (Layer 4)
- wachtdienst.md: WAT-conform guard duty order (Layer 4)
- All templates support ADF/Berrm mode markers"
```
