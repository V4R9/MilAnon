# Skeleton: Traktandenliste Einheitsrapport im Einsatz (Dok 060)
# Source: BFE_Vorlage_Einh_Rap_Einsatz_d.docx + BFE 52.080 Kap 4
# Usage: Checklist for the company rapport during operations.
#        Structured as a recurring meeting — typically daily or as needed.
#        Claude fills from current situation + Kdt decisions.
#
# DOCX Style Mapping:
#   ## Subject heading → "Subject heading" (Titel)
#   ### 1. Main title  → "1. Main title" (Hauptblöcke)
#   #### 1.1 Title     → "1.1 Title" (Traktanden)
#   - Bullet           → "Bullet List 1" (Unterpunkte)
#   Text               → "Text Indent" (Fliesstext)
#
# MODE MARKERS:
#   <!-- ADF: ... -->   = Only in ADF mode
#   <!-- BERRM: ... --> = Only in Berrm mode
#   <!-- FILL: ... -->  = Claude fills from current situation
#   <!-- KDT ENTSCHEID: ... --> = Commander must decide here

{einheit_bezeichnung}
{grad_kdt} {name_kdt}

{standort}, {datum} {zeit}

## Traktandenliste Einheitsrapport im Einsatz

Rapport Nr: <!-- FILL: Laufende Nummer -->
Ort: <!-- FILL: Rapportraum -->
Teilnehmer: Kp Kdt, Zfhr, Fachof (Fhr Ustü, San, Log, Sich)

---

### 1 Einführung

#### 1.1 Ziel des Rapports
- Aktualisierung Lagebild
- Befehlsausgabe für die nächste Phase
- Koordination der Elemente

#### 1.2 Sofortmassnahmen (SOMA) — Pendenzen
- <!-- FILL: Status der angeordneten Sofortmassnahmen -->
- <!-- FILL: Offene Pendenzen aus dem letzten Rapport -->

| Nr | Pendenz | Verantwortlich | Status |
|---|---|---|---|
| 1 | <!-- FILL --> | <!-- FILL --> | <!-- FILL: offen / erledigt --> |
| 2 | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
| 3 | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |

### 2 Lageverfolgung

#### 2.1 Nachrichtenlage
- <!-- FILL: Neue Erkenntnisse seit letztem Rapport -->
- <!-- FILL: Feindliche / gegnerische Aktivitäten -->
- <!-- FILL: Beobachtungen der Posten und Patrouillen -->
<!-- BERRM: Meldungen aus dem Interessenraum, zivile Quellen -->

#### 2.2 Eigene Lage
- <!-- FILL: Bestände (Personal, Material) -->
- <!-- FILL: Zustand der Truppe (Moral, Müdigkeit, Gesundheit) -->
- <!-- FILL: Einsatzbereitschaft der Elemente -->

#### 2.3 Nachbar-Lage
- <!-- FILL: Status Nachbar links -->
- <!-- FILL: Status Nachbar rechts -->
- <!-- FILL: Relevante Veränderungen -->

#### 2.4 Logistische Lage
- <!-- FILL: Versorgungslage (Munition, Verpflegung, Material) -->
- <!-- FILL: Sanitätslage -->
- <!-- FILL: Fahrzeuglage -->

#### 2.5 Führungsunterstützung
- <!-- FILL: Status Verbindungen -->
- <!-- FILL: Probleme mit Funk / Telefon -->

### 3 Entschluss

#### 3.1 Beurteilung der Lage (Kurzform)
<!-- KDT ENTSCHEID: Kdt beurteilt die aktuelle Lage und Handlungsoptionen -->
- <!-- FILL: Was hat sich verändert? -->
- <!-- FILL: Welche Optionen bestehen? -->

#### 3.2 Absicht Kp Kdt
<!-- KDT ENTSCHEID: Absicht für die nächste Phase -->
Ich will
- <!-- FILL: Absicht in 2-3 Punkten -->

#### 3.3 Aufträge

<!-- KDT ENTSCHEID: Aufträge an die Elemente für die nächste Phase -->

| Element | Auftrag | Ab | Bis |
|---|---|---|---|
| {element_1} | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
| {element_2} | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
| {element_3} | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
| Reserve | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
<!-- BERRM: Einsatzelement / Reserveelement / Ruheelement gemäss Dienstrad -->

#### 3.4 Besondere Anordnungen
- <!-- FILL: Änderungen ROE/ROB -->
- <!-- FILL: Änderungen Verbindung -->
- <!-- FILL: Logistische Anordnungen -->
- <!-- FILL: Ablösungen / Dienstrad -->
<!-- BERRM: Rotation der Elemente im Dienstrad -->

### 4 Befehlsausgabe

#### 4.1 Befehle und Weisungen
- <!-- FILL: Formelle Befehle die erlassen werden -->
- <!-- FILL: Verweis auf schriftliche Befehle falls vorhanden -->

#### 4.2 Koordination
- <!-- FILL: Zeitliche Koordination der Elemente -->
- <!-- FILL: Synchronisationspunkte -->

### 5 Abschluss

#### 5.1 Pendenzen (neu)

| Nr | Pendenz | Verantwortlich | Termin |
|---|---|---|---|
| 1 | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
| 2 | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |
| 3 | <!-- FILL --> | <!-- FILL --> | <!-- FILL --> |

#### 5.2 Nächster Rapport
- Zeitpunkt: <!-- FILL: Datum und Zeit -->
- Ort: <!-- FILL: gleich / anderer Ort -->
- Vorbereitung: <!-- FILL: Was müssen Zfhr mitbringen? -->

#### 5.3 Fragen
<!-- FILL: Raum für Fragen der Teilnehmer -->

### Verteiler
Geht an
- Teilnehmer Einheitsrapport
