# Aufgabe: Beurteilung der Lage (BFE 52.080 Kap 5.4)

Du erhältst die Produkte aus der Problemerfassung (Schritt 1) fuer {user_unit}.
Fuehre die Beurteilung der Lage gemaess BFE Kap 5.4 durch.

## Schritt 1: Vernetzte Faktorenanalyse (AUGEZ)

Analysiere systematisch die 5 Faktoren nach dem AEK-Schema (Aussage - Erkenntnis - Konsequenz).

### A -- Auftrag (BFE 5.4.1)

| | Aussagen | Erkenntnisse | Konsequenzen |
|---|---|---|---|
| **1. Bedeutung im Gesamtrahmen** | Absicht vorgesetzte Stufe (1+2 hoch) | Was bedeutet das fuer mich? | Mittel, Raeume, Zeit, Informationen (muss zeichenbar sein!) |
| **2. Erwartete Leistung** | Erhaltener Auftrag woertlich | min/max Leistung | Was muss ich MINDESTENS leisten? |
| **3. Handlungsspielraum** | gebunden / frei | Was kann ich selbst entscheiden? | Wo nutze ich die Freiheit? |
| **4. Unterstuetzung** | Ustue-Elemente, Nachbarn, Bat-Mittel | Was erhalte ich? Was muss ich anfordern? | Wie setze ich die Ustue ein? |

Falls die Auftragsanalyse bereits aus Schritt 1 vorliegt (`15_auftragsanalyse.md`), uebernimm sie und verfeinere sie.

### U -- Umwelt

- Gelaende: Schluesselgelaende, Hindernisse, Annaeherungswege, Sichtfelder
- Wetter / Licht / Jahreszeit
- Zivilbevoelkerung und Infrastruktur
<!-- BERRM: ZMZ-Analyse besonders wichtig: Gemeinde, Polizei, Schulen, Quartiermeister, zivile Akteure im Interessenraum -->
<!-- ADF: Uebungsgelaende, Sicherheitszonen, zivile Einschraenkungen -->

Produziere: Faktenplastik Umwelt (textuell beschrieben, auf Karte zeichenbar)

### G -- Gegner

- Staerke, Gliederung, Mittel
- **Bestimmende Lageentwicklungsmoeglichkeit** (gegnerische Hauptmoeglichkeit)
- Weitere Lageentwicklungsmoeglichkeiten
- **In allen Faellen** (permanente Bedrohungen)
<!-- BERRM: Gegner = reale Bedrohung: Sabotage, Aufklaerung, Info-Ops, Einwirkung auf Zivilbevoelkerung -->
<!-- ADF: Gegner gemaess Uebungsanlage / Bat Bf -->

Produziere: Bedrohungsplastik (textuell beschrieben, auf Karte zeichenbar)

### E -- Eigene Mittel

- Verfuegbare Verbaende, Material, Infrastruktur
- Staerken und Schwaechen
- Unterstuetzungselemente (Bat-Mittel, Nachbarn)

Produziere: Faktenplastik BLAU (textuell beschrieben, auf Karte zeichenbar)

### Z -- Zeit

- Zeitliche Verhaeltnisse (Deadlines, Phasen, Fristen)
- Synchronisation mit Bat-Zeitplan
- Verweis auf Synchronisationsmatrix aus Schritt 1 (`14_synchronisationsmatrix.md`)

## Schritt 2: Schluesselbereiche ableiten

### Schluesselbereiche ROT

- Wo und wie kann der Gegner entscheidend wirken?
- Kritische Punkte, Zeitfenster, Raeume fuer den Gegner
- Pro Schluesselbereich: konkrete gegnerische Handlung benennen

Produziere: Konsequenzenplastik ROT (textuell beschrieben, auf Karte zeichenbar)

### Schluesselbereiche BLAU

- Wo und wie koennen WIR entscheidend wirken?
- Eigene Optionen, Staerken ausnutzen, Schwaechen kompensieren
- Pro Schluesselbereich: konkrete eigene Handlungsoption benennen

Produziere: Konsequenzenplastik BLAU (textuell beschrieben, auf Karte zeichenbar)

## Schritt 3: Konsequenzen formulieren

### Konsequenzen ROT -- Was muss ich VERHINDERN?

- Pro Schluesselbereich: Gegenmassnahmen ableiten
- Nummerierung beibehalten (wird in Schritt 3 Entschlussfassung referenziert)

### Konsequenzen BLAU -- Was muss ich TUN?

- Pro Schluesselbereich: eigene Handlungsoptionen
- Kategorien: **Mittel, Raeume, Zeit, Informationen** (muss zeichenbar sein!)
- Nummerierung beibehalten (wird in Schritt 3 fuer Variantenbildung verwendet)

## Markierungen

- Verwende `<!-- KDT ENTSCHEID: ... -->` wo der Kommandant persoenlich entscheiden muss
- Verwende `<!-- FILL: ... -->` wo Informationen aus dem Bat Bf oder der Erkundung fehlen

## Output

Produziere folgende Dateien (jeweils mit `# Dateiname` als Header, getrennt durch `---`):

1. `20_augez_analyse.md` -- Vollstaendige AUGEZ-Analyse mit allen 5 Faktoren (AEK-Schema)
2. `21_schluesselbereiche.md` -- Schluesselbereiche ROT + BLAU mit Konsequenzenplastik
3. `22_konsequenzen.md` -- Konsequenzen ROT + BLAU (nummeriert, zeichenbar!)
4. `23_mittelbedarfsrechnung.md` -- Falls Antraege an Bat noetig (optional)

WICHTIG: Alle [PLACEHOLDER]-Token exakt beibehalten. Keine Originalnamen, Orte oder Einheitsbezeichnungen rekonstruieren.
