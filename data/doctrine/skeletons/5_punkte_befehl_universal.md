# Skeleton: 5-Punkte-Befehl Stufe Einheit (Universal)
# Source: CH Armee Befehl Vorlage (DOCX) + BFE 52.080 Kap 5.7.1
# Works for: ADF (klassischer WK) AND Berrm (Bereitschaftsraum)
# The structure is IDENTICAL — only the CONTENT differs per mode.
#
# DOCX Style Mapping:
#   # Heading 1       → "Heading 1" (Grundlagen)
#   ## Subject heading → "Subject heading" (Deckname, bold, 13pt)
#   ### 1. Main title  → "1. Main title" (Hauptpunkte 1-5)
#   #### 1.1 Title     → "1.1 Title" (Unterpunkte)
#   ##### 1.1.1 Title  → "1.1.1 Title" (Sub-Unterpunkte)
#   Text               → "Text Indent" (Fliesstext)
#   - Bullet           → "Bullet List 1"
#   | Table |           → Table (for Aufträge, Standorte)
#
# MODE MARKERS:
#   <!-- ADF: ... -->   = Only include in ADF mode (klassischer WK)
#   <!-- BERRM: ... --> = Only include in Berrm mode
#   <!-- BOTH: ... -->  = Include in both modes
#   <!-- KDT ENTSCHEID: ... --> = Commander must decide here
#   <!-- FILL: ... -->  = Claude fills from Bat Bf or BdL products

# ============================================================================
# HEADER
# ============================================================================

{einheit_bezeichnung}
{grad_kdt} {name_kdt}

{standort}, {datum}

## "{deckname}"

<!-- ADF: Optional — Übungstitel wenn Einsatzbefehl für Verbandsübung -->
<!-- BERRM: Kein Übungstitel — dies ist der Grundbefehl -->

# Grundlagen

- {grundlage_1};
- {grundlage_2};
- {grundlage_n}.
<!-- FILL: Alle referenzierten Reglemente und Bat-Dokumente auflisten -->
<!-- BOTH: BFE 52.080 ist immer Grundlage -->
<!-- BERRM: 53.005.21 (Ei Verf Bat) und 53.005.23 (Ei Verf Kp) zusätzlich -->

# ============================================================================
# PUNKT 1 — ORIENTIERUNG / LAGE
# ============================================================================

### 1 Orientierung

<!-- FILL: 2-3 Sätze Kontext — Gesamtlage, was für ein Dienst, Rahmen -->
<!-- BERRM: "Im Rahmen der Bereitschaft erstellt und betreibt das Inf Bat 56 
     einen dezentralen Bereitschaftsraum im Raum [ORT]..." -->
<!-- ADF: "Im Rahmen des WK {jahr} führt das Inf Bat 56 den Ausbildungsdienst 
     im Raum [ORT] durch..." -->

#### 1.1 Bedrohung
<!-- BERRM: Echte Bedrohungsanalyse für den Berrm-Raum. 
     ZMZ und Zivilbevölkerung als Faktor. -->
<!-- ADF: Bedrohung gemäss Übungsanlage ODER aus Bat Sicherheitsbefehl -->

##### 1.1.1 Bestimmende Lageentwicklungsmöglichkeit
<!-- FILL: Aus Bat Bf oder eigener BdL -->

##### 1.1.2 Weitere Lageentwicklungsmöglichkeiten
<!-- FILL: Aus Bat Bf oder eigener BdL -->

##### 1.1.3 In allen Fällen
<!-- FILL: Permanente Bedrohungen -->
<!-- BERRM: Aufklärung, Sabotage, Info-Ops, Einwirkung auf Zivilbevölkerung -->

#### 1.2 Erhaltener Auftrag
<!-- FILL: Direkt aus Bat Bf extrahieren — alle Aufträge für {einheit} -->
<!-- BERRM: Muss die 3 Phasen abdecken (Bezug → Erhalten → Raumerweiterung) -->
<!-- ADF: Ausbildungs- und Einsatzaufträge gemäss Bat Bf -->

#### 1.3 Nachbartruppen und Partner
<!-- FILL: Nachbar-Kp und deren Aufträge -->
<!-- BERRM: Zusätzlich zivile Partner (Gemeinde, Polizei, Feuerwehr, QM) -->

# ============================================================================
# PUNKT 2 — ABSICHT
# ============================================================================

### 2 Absicht

Ich will

<!-- KDT ENTSCHEID: Der Kdt formuliert seine eigene Absicht -->
<!-- BERRM: Absicht MUSS die 3 Phasen des Berrm abdecken: -->
<!--   Phase 1: Bezug und Erstellen der Einsatzbereitschaft -->
<!--   Phase 2: Erhalten der Einsatzbereitschaft (Dienstrad) -->
<!--   Phase 3: Raumerweiterung in den Interessenraum -->
<!-- ADF: Absicht deckt die WK-Phasen ab: -->
<!--   KVK/Einrücken → Ausbildung → Einsatz/Übung → WEMA -->

<!-- SUGGEST: Claude schlägt Absicht vor basierend auf Auftrag und BdL -->

# ============================================================================
# PUNKT 3 — AUFTRÄGE
# ============================================================================

### 3 Aufträge

<!-- KDT ENTSCHEID: Aufträge an Züge/Funktionen — taktische Aufgaben verwenden! -->
<!-- NUR offizielle Verben: sperren, halten, sichern, bewachen, überwachen... -->
<!-- Auftragstaktik: WAS, nicht WIE — max Handlungsfreiheit -->

<!-- BERRM: Aufträge orientieren sich am Dienstrad -->
<!--   Phase 1 (Bezug): Wer sichert, wer bezieht, wer erkundet -->
<!--   Ab Phase 2: Einsatzelement / Reserveelement / Ruheelement (rotierend) -->

<!-- ADF: Aufträge orientieren sich am WAP / Ausbildungsphasen -->
<!--   Kdo Z, Inf Z 1-3, Mw Z — klassische Gliederung -->

#### 3.1 {element_1}
<!-- FILL: Auftrag für Element 1 -->

#### 3.2 {element_2}
<!-- FILL: Auftrag für Element 2 -->

#### 3.3 {element_3}
<!-- FILL: Auftrag für Element 3 -->

<!-- Bei Bedarf: Tabelle für übersichtliche Darstellung -->
| Element | Auftrag |
|---|---|
| {element_1} | {auftrag_1} |
| {element_2} | {auftrag_2} |
| {element_3} | {auftrag_3} |

# ============================================================================
# PUNKT 4 — BESONDERE ANORDNUNGEN
# ============================================================================

### 4 Besondere Anordnungen

#### 4.1 Rahmenbereiche

##### 4.1.1 Recht / ROE, ROB
<!-- FILL: Aus Bat Bf -->
<!-- BERRM: Verhalten ggü Zivilbevölkerung, Eskalationsstufen, 
     im Dialog mit ziv Behörden erarbeitet -->
<!-- BOTH: Gem Beilage Pocketcard ROE/ROB -->

##### 4.1.2 Kommunikation
- Es dürfen keine Informationen an Externe weitergegeben werden (TOZZA).
<!-- BERRM: Schlüsselnachrichten an Zivilbevölkerung, Behördenkontakt -->

##### 4.1.3 Personalwesen
<!-- FILL: Organigramm, Stellvertretung -->

##### 4.1.4 Integrale Sicherheit
Es gilt das Regl 52.569 "Integrale Sicherheit".

#### 4.2 Nachrichtendienst

##### 4.2.1 Besondere Nachrichtenbedürfnisse
<!-- FILL: Aus BdL-Produkte — was beobachten und melden -->
<!-- BERRM: Komplementarität der Sensoren — 
     überbaut: primär zivile Quellen; Zwischengelände: primär mil Mittel -->

#### 4.3 Einsatz

##### 4.3.1 Abschnittsgrenzen
Gem Beilage.
<!-- BERRM: Zugsräume im Berrm, Interessenraum-Grenzen -->

##### 4.3.2 Territoriale Aufgaben / ZMZ
<!-- BERRM: Regelung Zusammenleben mil/ziv, Checkpoints, Warnschilder,
     Kontaktpersonen für ziv Behörden -->
<!-- ADF: Behördenkontakt, Nutzung ziv Infrastruktur -->

##### 4.3.3 Eventualplanung
<!-- BERRM: 2 Pflicht-EP: Halten Standort + Kampf Interessenraum -->
<!-- ADF: Falls vorhanden — oft nur für Verbandsübung -->
Gem Beilage(n).

##### 4.3.4 Feuerunterstützung
<!-- FILL: Mw-Einsatz, Feuerräume -->

##### 4.3.5 Bewegungs- und Hindernisführung
<!-- BERRM: Checkpoints, minimale Härtungen -->

##### 4.3.6 ABC
<!-- FILL: Bereitschaftsgrad -->

##### 4.3.7 Truppenschutzmassnahmen
<!-- FILL: Tarnung, Deckung -->

##### 4.3.8 Synchronisationsmatrix
Gem Beilage.

#### 4.4 Logistik

##### 4.4.1 Nachschub
<!-- FILL: Versorgungskonzept -->
<!-- BERRM: Phase 1 dezentral → Phase 2 zentralisiert -->

##### 4.4.2 Instandhaltung
<!-- FILL -->

##### 4.4.3 Sanitätsdienst
<!-- FILL: Evakuierungskette -->

##### 4.4.4 Verkehr und Transport
<!-- FILL -->

##### 4.4.5 Infrastruktur
<!-- BERRM: Nutzung bestehender ziv Infra für Führung und Leben -->

#### 4.5 Durchhaltefähigkeit
<!-- BERRM: ZENTRAL — Dienstrad (Dreier-/Vierergliederung, Ablöserhythmus) -->
<!-- ADF: Wechsel Einsatz/Ruhe/Ausbildung gemäss WAP -->

#### 4.6 Führungsunterstützung
<!-- FILL: Verbindungen, ANP, Funknetze -->
<!-- BERRM: TBG SEEin + Feldtelefon für Festinstallationen -->

#### 4.7 Ausbildung
<!-- BERRM: Mittel zum Zweck — EBA im Reserveelement, AGA-Rep in Ablösezyklen -->
<!-- ADF: Verweis auf Bf Ausbildung (eigenes Dokument) -->
Gem Erg Bf Ausbildung.

# ============================================================================
# PUNKT 5 — STANDORTE
# ============================================================================

### 5 Standorte

| Stelle | Standort | Telefon |
|---|---|---|
| KP {bat} | <!-- FILL --> | <!-- FILL --> |
| KP {einheit} | <!-- FILL --> | <!-- FILL --> |
<!-- BERRM: Zugsräume, San-Posten, Fz-Park -->
<!-- ADF: KP, Ukft, Ausbildungsplätze -->

{grad_kdt} {name_kdt}
Kommandant

# ============================================================================
# BEILAGEN
# ============================================================================

Beilage(n)

<!-- BERRM: Typische Beilagen -->
<!-- 1. Lageentwicklungsmöglichkeiten (Plastik) -->
<!-- 2. Abschnittsgrenzen mit Zugsräumen + Interessenraum (Plastik) -->
<!-- 3. Führungsraster -->
<!-- 4. Einsatzunterstützung (Plastik) -->
<!-- 5. Pocket Card ROE/ROB -->
<!-- 6. EP 1 — Halten des Standorts -->
<!-- 7. EP 2 — Kampf im Interessenraum -->
<!-- 8. Synchronisationsmatrix -->
<!-- 9. Adressnetzplan -->
<!-- 10. Ausbildungskonzept -->
<!-- 11. Dienstrad-Schema -->

<!-- ADF: Typische Beilagen -->
<!-- 1. Lageentwicklungsmöglichkeiten (Plastik) -->
<!-- 2. Abschnittsgrenzen (Plastik) -->
<!-- 3. Führungsraster -->
<!-- 4. Einsatzunterstützung (Plastik) -->
<!-- 5. Pocket Card ROE/ROB -->
<!-- 6. Leistungskatalog -->
<!-- 7. Synchronisationsmatrix -->
<!-- 8. Adressnetzplan -->
<!-- 9. Ausbildung -->

# ============================================================================
# VERTEILER
# ============================================================================

Geht an
- Höh Kader {einheit}
- Truppe (via Anschlag)
z K an
- Kdt {bat}
