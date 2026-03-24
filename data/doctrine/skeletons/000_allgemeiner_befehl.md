# Skeleton: Allgemeiner Befehl (Dok 000)
# Source: Dossier 2020 Inf Kp 56/3 + BFE 52.080 Kap 5.3
# Usage: Claude fills in the fields based on the Bat Dossier

Kdt {unit}

{ort}, {datum}

"{deckname}"

## Allgemeiner Befehl für den WK {jahr}
LK 1:50'000; BI {kartenblätter}

### Orientierung
<!-- FILL: 2-3 Sätze Kontext — wann, wo, was für ein Dienst -->

### Grundlagen
<!-- FILL: Alle referenzierten Reglemente und Bat-Dokumente auflisten -->
- Regl 51.002, Dienstreglement DR 04;
- Regl 51.019, Grundschulung 17 (GS 17);
- {bat_name}: Befehlsdossier für den KVK / WK {jahr};
- {bat_name}: Befehlsausgabe vom {datum_ba} des Kdt {bat_name};
<!-- FILL: Weitere Grundlagen aus dem Bat Dossier -->

### Absicht der vorgesetzten Kommandostelle
Der Kdt {bat_name} will
<!-- FILL: Direkt aus dem Bat Befehl extrahieren — die Absicht des Bat Kdt -->
<!-- STRUCTURE: Phasenweise (In einer ersten Phase... In einer zweiten Phase...) -->

### Erhaltener Auftrag
<!-- FILL: Alle Aufträge aus dem Bat Bf die {unit} direkt betreffen -->
<!-- FORMAT: Aufzählung mit Semikolon-Trennung -->

### Standorte eigene Truppen
<!-- FILL: KP-Standort, Ukft, Ausbildungsplätze — aus Bat Dossier + Erkundung -->

### Absicht
Ich will
<!-- KDT ENTSCHEID: Der Kdt formuliert seine eigene Absicht basierend auf dem erhaltenen Auftrag -->
<!-- SUGGEST: Claude schlägt eine Absicht vor basierend auf den Aufträgen — phased structure -->
<!-- STRUCTURE: im KVK...; nach Einrücken...; im Einsatz...; in der letzten Phase... -->

### Aufträge
<!-- KDT ENTSCHEID: Aufträge an Züge/Funktionen — Kdt muss Zuordnung bestimmen -->
<!-- SUGGEST: Claude schlägt Zuordnung vor basierend auf Absicht und Bat-Vorgaben -->

### Besondere Anordnungen

#### Personelles
<!-- FILL: Organigramm-Referenz, besondere Personalregelungen -->

#### Seelsorge
Termine mit dem Armeeseelsorger sind auf dem Dienstweg via Zfhr → Kp Kdt zu vereinbaren. In Notfällen direkter Kontakt unter der Nummer <!-- FILL: Telefonnummer Armeeseelsorger -->.

#### Weisungen Presse und Information
- Anfragen von Medienvertretern sind an den PIO {bat_name} weiterzuleiten;
- Jegliche Auskunftserteilung an Externe ohne ausdrückliche Erlaubnis des Bat bzw. Kp Kdt ist untersagt.

#### Aufnahmen Bild- und Tonmaterial
<!-- STANDARD: Text aus DR 04 — Verbot ohne Einwilligung Kdt -->
Angehörige der Armee dürfen im Militärdienst ohne Einwilligung des Kommandanten weder fotografieren noch Filme und Videosequenzen aufnehmen. Insbesondere ist es generell verboten, Bilder oder Videosequenzen in irgendeinem Medium zu veröffentlichen. Diesbezügliche Verstösse werden disziplinarisch geahndet.

### Ausbildung, Wachtdienst, Eigenschutz und Integrale Sicherheit

#### Ausbildung
Gem Beilage 200 "Befehl für die Ausbildung".

#### Wachtdienst
Gem Beilage 300 "Wachtdienstbefehl {standort_a}" <!-- FILL: und ggf 400 für Standort B -->

#### Eigenschutz
<!-- FILL: Verweis auf Bat Eigenschutz-Befehl (Deckname + Bedrohungsstufen) -->
<!-- STANDARD: Grundschutz gem Regl 52.569 "Integrale Sicherheit" -->
- TOZZA Prinzip (keine Preisgabe von Informationen);
- Eintretende Personen und Fahrzeuge identifizieren;
- Schutzwürdiges Material ständig bewachen.

#### Integrale Sicherheit
Es gilt das Reglement 52.569 "Integrale Sicherheit".
<!-- FILL: Zutrittsschutz, Informatik/Informatiksicherheit, Datenschutz -->

### Standorte / Führungseinrichtungen
<!-- FILL: Tabelle mit KP-Standorten (Bat + eigene Kp) -->

| Formation | Standort | Telefon |
|---|---|---|
| {bat_name} | <!-- FILL --> | <!-- FILL --> |
| {unit} | <!-- FILL --> | <!-- FILL --> |

{grad_kdt} {name_kdt}
Kommandant

### Beilagen
<!-- FILL: Nummerierte Liste aller Beilagen — Standardstruktur: -->
001 Kp Organigramm
002 Wochenarbeitsplan (Picasso)
003 Karte WK Raum {standort_a}
<!-- 004 Karte WK Raum {standort_b} — falls 2 Standorte -->
005 Telefonliste {unit}
<!-- 006-007 Erkundungsberichte — falls vorhanden -->
008 Terminliste
009 Befehl für die Notfall-Alarmierung {standort_a}
010 Schema für die Notfall-Alarmierung
100 Befehl für den Dienstbetrieb inkl Beilagen
200 Befehl für die Ausbildung inkl Beilagen
300 Wachtdienstbefehl {standort_a} inkl Beilagen
<!-- 400 Wachtdienstbefehl {standort_b} — falls 2 Standorte -->
500 Einsatzbefehl inkl Beilagen

### Verteiler
Geht an
- Höh Kader
- Truppe (via Anschlag)
z K an
- Kdt {bat_name}
