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

## Schritt 1b: Auftragsanalyse (BFE 5.4.1)

Erstelle die Auftragsanalyse in der fixen Tabellenstruktur:

| | Aussagen | Erkenntnisse | Konsequenzen |
|---|---|---|---|
| **1. Bedeutung der Aufgabe im Gesamtrahmen** | Absicht vorgesetzte Stufe (1+2 Stufen hoch) | Was bedeutet das für mich? | Mittel, Räume, Zeit, Informationen (muss zeichenbar sein!) |
| **2. Erwartete Leistung des Verbandes** | Erhaltener Auftrag wörtlich | min: Mindestleistung / max: Maximalleistung | Was muss ich MINDESTENS leisten? |
| **3. Handlungsspielraum** | gebunden: Was ist FIX vorgegeben / frei: Wo habe ich Freiheit | Was kann ich selbst entscheiden? | Wo nutze ich die Freiheit? |
| **4. Direkte + Indirekte Unterstützung** | Welche Ustü-Elemente, Nachbarn, Bat-Mittel | Was erhalte ich? Was muss ich anfordern? | Wie setze ich die Ustü ein? |

WICHTIG: Die Konsequenzen in Zeile 1 müssen in die Kategorien **Mittel, Räume, Zeit, Informationen** gegliedert sein und müssen auf der Planungskarte **zeichenbar** sein.

Produziere: `15_auftragsanalyse.md`

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
9. `15_auftragsanalyse.md`

WICHTIG: Alle [PLACEHOLDER]-Token exakt beibehalten. Keine Originalnamen, Orte oder Einheitsbezeichnungen rekonstruieren.
