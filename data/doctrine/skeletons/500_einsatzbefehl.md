# Skeleton: Kp Einsatzbefehl (Dok 500)
# Source: Kp_Einsatzbefehl_U_HERMES_CINQUE + Kp_Einsatzbefehl_U_CONEX_20 + BFE 52.080
# Usage: Claude fills in based on Bat Einsatzbefehl + taktische Lage

Kdt {unit}

{standort}, {datum}

"{deckname}"

## Kp Einsatzbefehl "{übungsname}"
LK 1:{massstab}; {kartenreferenz}

### Orientierung

#### Allgemeine Lage
<!-- FILL: Aus Bat Ei Bf — kurze Zusammenfassung der Gesamtlage -->

#### Bedrohung / Gegnerische Möglichkeiten

##### Bestimmende gegnerische Möglichkeit
Der Gegner kann:

**In einer ersten Phase:**
<!-- FILL: Aus Bat Bf + eigene Beurteilung -->
<!-- STRUCTURE: Zeitliche Verhältnisse, Mittel, Raum, Absicht des Gegners -->

**In einer zweiten Phase:**
<!-- FILL: Eskalationsstufe -->

##### Weitere gegnerische Möglichkeiten
Ausserdem kann der Gegner:
<!-- FILL: Alternative gegnerische Handlungsmöglichkeiten -->

##### In allen Fällen
Kann der Gegner:
<!-- FILL: Permanente Bedrohungen (Informationskampagnen, Aufklärung, etc.) -->

#### Absicht vorgesetzter Kommandant (Kdt {bat_name})
Der Kdt {bat_name} will:
<!-- FILL: Direkt aus Bat Ei Bf extrahieren -->
<!-- STRUCTURE: Phasenweise, mit allen Kp-Aufträgen -->

#### Erhaltener Auftrag ({unit})
<!-- FILL: Alle Aufträge aus Bat Ei Bf die {unit} direkt betreffen -->

#### Nachbartruppen
<!-- FILL: Nachbar-Kp und deren Aufträge — links, rechts, hinten -->

### Absicht
Ich will:

**In einer ersten Phase** und nach Abschluss der Ausbildung:
<!-- KDT ENTSCHEID: Eigene Absicht Phase 1 -->
<!-- SUGGEST: Claude schlägt vor basierend auf erhaltenem Auftrag -->

**In einer zweiten Phase:**
<!-- KDT ENTSCHEID: Eigene Absicht Phase 2 -->

**In einer dritten Phase:**
<!-- KDT ENTSCHEID: Eigene Absicht Phase 3 -->

**Über alle Phasen:**
<!-- FILL: Querschnittsaufgaben (Wachtdienst, Nachrichten, etc.) -->

### Aufträge

#### Für die erste Phase:
<!-- FILL: Aufträge an Züge/Elemente — pro Phase -->

| Element | Auftrag |
|---|---|
| <!-- FILL: Z/El Name --> | <!-- FILL: Auftrag --> |

#### Für die zweite Phase:
<!-- FILL -->

#### Für die dritte Phase:
<!-- FILL -->

### Besondere Anordnungen

#### Rahmenbereiche / Rechtliche Handlungsrichtlinien (ROE/ROB)
<!-- FILL: Aus Bat Bf — Einsatzregeln, KVR, Verhältnismässigkeit -->
Alles Weitere gem Beilage Pocketcard ROE/ROB

#### Nachrichtendienst

##### Über alle Phasen:

###### Besondere Nachrichtenbedürfnisse (BNB)
<!-- FILL: Was muss die Kp beobachten und melden -->
- Informationen über gegnerische Kräfte, Gliederung, Führungsstrukturen;
- Zeitliche Verhältnisse und Stossrichtungen im Eirm;
- Anzeichen koordinierter Aktionen des Gegners.

###### Meldungen
<!-- FILL: Standardmeldungen -->
Meldung wenn: Abmarsch, WP passiert, Berrm erreicht, Reorg/WEB beendet.

#### Funkverbindungen
<!-- FILL: Aus Bat ANP -->
- Kp – Z via Se <!-- FILL: Kanal -->
- Z – Gr via Se <!-- FILL: Kanal -->

### Einsatz

#### Raumordnung
<!-- FILL: Verweis auf Bat Raumordnung + eigene Kp Raumordnung -->
Raumordnung {bat_name}: gem Beilage
Raumordnung {unit}: gem beso Bf Kp Kdt Stv / Einh Fw

#### Marschreihenfolge
<!-- FILL: Vorhut, Gros, Nachhut — falls Verschiebung geplant -->

#### Führungskarte
Gem Beilage Kp Führungskarte

#### Eventualplanung
<!-- FILL: Aus Bat Bf oder eigene — falls nicht: "Absichtlich leer." -->

#### Bewegungs- und Hindernisführung
<!-- FILL: Falls relevant — sonst "Absichtlich leer." -->

#### ABC
<!-- FILL: Bedrohungslage ABC -->

#### Einsatzbezogene Ausbildung
Gem Beilage Arbeitsprogramm

#### Wachtdienst
Gem Beilage Einsatzbefehl für den Wachtdienst

### Logistik

#### Nach- und Rückschub aller Klassen
<!-- FILL: Versorgungskonzept — von Bat Logistikpunkt bis Kp/Z -->

#### Durchhaltefähigkeit
<!-- FILL: Verantwortlichkeiten -->
- Four: Verantwortlich für Vpf Durchhaltefähigkeit;
- Fw: Verantwortlich für Log Durchhaltefähigkeit (Mat Fsg/Ret);
- Kp Kdt Stv: Verantwortlich für Wacht Durchhaltefähigkeit.

#### Kriegsgefangenenwesen
<!-- FILL: Falls Einsatz-Szenario — Personalienerfassung, Transport -->

#### Sanitätsdienst Eigene
<!-- FILL: Evakuierungskette -->
1. Prio: Selbst- und Kameradenhilfe, Verwundeten Sammelstelle Stufe Kp/Z
2. Prio: Stufe Bat; San Hist <!-- FILL: nächste San Einrichtung -->
3. Prio: <!-- FILL: nächstes Spital -->

#### Sanitätsdienst Gegner
<!-- FILL: Gleiche Kette, zusätzlich KVR-konforme Behandlung -->

#### Verkehr und Transport
<!-- FILL: Konvoy-Regeln, Autobahn-Bewilligungen, Selbstschutz -->

### Standorte der Führungseinrichtungen
<!-- FILL: KP-Standort(e) der Kp -->

| Formation | Standort | Telefon |
|---|---|---|
| {unit} | <!-- FILL --> | <!-- FILL --> |

{grad_kdt} {name_kdt}
Kommandant

### Beilagen
<!-- FILL: Nummerierte Beilagen -->
1. Pocketcard ROE / ROB
2. Bat Raumordnung
3. Kp Führungskarte(n)
4. Eventualplanungen
5. Arbeitsprogramm
6. Einsatzbefehl für den Wachtdienst
<!-- FILL: Weitere nach Bedarf -->

### Verteiler
Geht an:
- Höh Kader {unit}
z K an:
- Kdt {bat_name}
