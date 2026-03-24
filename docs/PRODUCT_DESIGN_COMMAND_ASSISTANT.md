# MilAnon Command Assistant — Product Design v3.1

> Based on: BFE 52.080 Kap 5, FSO 17 Kap 4.2, **TF 50.030 Kap 5** (fully integrated), cross-referenced
> Plus: Dossier 2020 (Inf Kp 56/3), 4 Einsatzbefehle, 3 Wachtdienst-Vorlagen, 12 Reglemente
> Author: Product Design Session 2026-03-25
> Status: Design complete — 5+2 + TF 17 taktische Grundlagen als zentrales Konzept
> 
> **This document has 2 parts:**
> - Part 1 (this file): 5+2 Process Design, Workflow Architecture, Product Comparison
> - Part 2: [PRODUCT_DESIGN_TF17_APPENDIX.md](PRODUCT_DESIGN_TF17_APPENDIX.md) — Tactical Knowledge Base (Einsatzgrundsätze, Taktische Grundsätze, Raumordnung, Taktische Aufgaben, Auftragstaktik, Updated System Prompt)

---

## 1. The 5+2 — Deep Understanding

### Source: FSO 17 Zif 113 + BFE 52.080 Kap 5

The 5+2 is a **rational decision-making process** (FSO Zif 111) designed to work under time pressure, uncertainty, and incomplete information. It is the universal methodology that every Swiss Army commander applies — from Corps to Squad level.

On **Stufe Einheit** (Company), the commander works **alone** (BFE S.491) — no staff. This is the fundamental difference to Battalion/Brigade level. The BFE translates the FSO's staff-level process into a one-person workflow with physical tools (map, plastic overlays, notebook).

MilAnon's job: **Be the digital staff** that the Kp Kdt doesn't have.

### The Complete 5+2 Structure (BFE 52.080 Kap 5)

```
5 AKTIONSPLANUNG

  5.1 Führungstätigkeit: PROBLEMERFASSUNG
      5.1.1 Initialisierung
            → Einsatzbefehl lesen + 4-Farben-Markierung
            → Übersichtskarte erstellen
            → Planungskarte erstellen (6 Plastik-Folien)
      5.1.2 Problemerfassung
            → Problementdeckung (IST→SOLL, worum geht es?)
            → Problemklärung (Teilprobleme, Aufgaben, Handlungsrichtlinien, Produkte)
            → Problembeurteilung (Prioritäten, Delegation)
            → Interner + externer Zeitplan auf Synchronisationsmatrix

  5.2 Führungstätigkeit: SOFORTMASSNAHMEN
      → OEBAS-VIV: Orientierung, Erkundung, Befehlsgebungsvorbereitung,
                    Alarmierung, Sicherung, Verbindungsaufnahme,
                    Inmarschsetzung, Vorausaktionen
      → Gefechtsjournal (Form 06.070) für SOMA
      → Notizheft für Pendenzen
      → Eisenhower-Prinzip (Wichtig/Dringend Matrix)

  5.3 Führungstätigkeit: ZEITPLANUNG
      → Synchronisationsmatrix (interner + externer Zeitplan)
      → Viertelregel: ¼ eigene Planung, ¾ für Unterstellte (FSO Zif 139)
      → Rückwärtsplanung vom Wirkungszeitpunkt

  5.4 Führungstätigkeit: BEURTEILUNG DER LAGE (BdL)
      5.4.1 Vernetzte Faktorenanalyse
            → AUGEZ-Faktoren: Auftrag, Umwelt, Gegner, Eigene, Zeit
            → AEK-Methode: Aussage → Erkenntnis → Konsequenz (FSO Zif 152-154)
            → 3 Arbeitsschritte:
              1. Aussagen sammeln (Fakten auf Faktenplastik)
              2. Erkenntnisse gewinnen (Vernetzung der Faktoren — Pentagramm)
              3. Konsequenzen ableiten (ROT und BLAU, nach KRZI)
            → Schlüsselbereiche ROT + BLAU identifizieren
            → "Aus ROT mach BLAU" Prinzip
      5.4.2 Herleitung und Erarbeitung der Bedrohung
            → Bestimmende Lageentwicklungsmöglichkeit
            → Weitere Lageentwicklungsmöglichkeiten
            → In allen Fällen
      5.4.3 Mittelbedarfsrechnung/Leistungskatalog (für KI)

  5.5 Führungstätigkeit: ENTSCHLUSSFASSUNG
      5.5.1 Herleitung und Erarbeitung von eigenen Möglichkeiten
            → Varianten generieren aus Konsequenzen BLAU
            → Echte Varianten unterscheiden sich durch ROS:
              R = Reserve (wie wird Reserve eingesetzt)
              O = Organisation (wie sind Kräfte gegliedert)
              S = Schwergewicht (wo liegt der Schwerpunkt)
            → Variantenprüfung nach FSO Zif 206:
              - Angemessenheit (entspricht Absicht vorgesetzter Kdt?)
              - Exklusivität (unterscheidet sich von anderen Varianten?)
              - Machbarkeit (Kräfte/Mittel ausreichend?)
              - Tragbarkeit (Risiken tragbar?)
              - Vollständigkeit (wann? wer? was? wo? wie?)
            → Bewertung nach Einsatzgrundsätzen (TF 17):
              Ausrichten auf Ziel, Schwergewicht, Einfachheit,
              Sicherheit, Ökonomie der Kräfte, Einheitlichkeit,
              Flexibilität, Freiheit des Handelns, Überraschung,
              Verhältnismässigkeit
      5.5.2 Entschluss
            → Gewählte Variante zum Entschlussplastik ausarbeiten
            → Reserveeinsätze für weitere Lageentwicklungsmöglichkeiten
            → Absicht formulieren ("Ich will...")
            → Aufträge an Unterstellte ableiten
            → "Erst die Unterstützungskonzepte und der Aktionsplan
               ermöglichen dem Kdt, aus dem Entschluss seine definitive
               Absicht zu formulieren" (FSO Zif 215)
      5.5.3 Mittelbedarfsrechnung/Leistungskatalog (Entschluss für KI)

  5.6 Führungstätigkeit: PLANENTWICKLUNG
      → Eventualplanung (FSO Zif 226-234):
        - Hypothetische AP für nicht berücksichtigte Lageentwicklungen
        - Vorbehaltene Entschlüsse (werden in Lageverfolgung ausgelöst)
        - Reserven bereiten sich auf verschiedene Aktionen vor
      → Unterstützungskonzepte (Beilagen):
        - Nachrichtendienst (BNB, ND-Auftrag)
        - Einsatz (Raumordnung, Hindernisse, ABC)
        - Einsatzunterstützung (Feuer, Mw, Pionier)
        - Logistik (Ns/Rs, San, Vpf, V+T)
        - Führungsunterstützung (Verbindungen, ANP, FIS HE)
      → Besondere Anordnungen:
        - Recht/ROE/ROB
        - Kommunikation/Presse
        - Personal
        - Integrale Sicherheit
      → Synchronisationsmatrix finalisieren

  5.7 Führungstätigkeit: BEFEHLSGEBUNG
      5.7.1 Einsatzbefehl der Einheit
            → 5-Punkte-Befehl zusammensetzen:
              1. Orientierung (Bedrohung, Erhaltener Auftrag, Nachbarn)
              2. Absicht
              3. Aufträge (pro Zug/Element)
              4. Besondere Anordnungen + Beilagen
              5. Standorte
            → Produkte werden WÄHREND der AP fortlaufend eingebaut
            → "Was in der AP nicht seriös vorbereitet wird, bleibt
               als Altlast in der Lageverfolgung" (BFE S.26)
      5.7.2 Befehlsgebung
            → Methodisch und kommunikativ geschickte Präsentation
            → Führungsbrett, Geländemodell, Signaturenkärtchen
```

### Cross-Reference: BFE → FSO

Every BFE chapter references the corresponding FSO section. The FSO provides the theoretical framework, the BFE the practical implementation:

| BFE Section | FSO Reference | What FSO adds |
|---|---|---|
| 5.1.1 Initialisierung | FSO Pt 4.2, Abb 10 | Overview of all 5+2 Führungstätigkeiten |
| 5.1.2 Problemerfassung | FSO Pt 4.2.1, Zif 118-129 | 3 Teilschritte: Entdeckung, Klärung, Beurteilung. Orientierungsrapport. Stabsgliederung. |
| 5.2 Sofortmassnahmen | FSO Pt 4.2.2, Zif 130-132 | "Dürfen weder dem Entschluss vorgreifen noch die Entschlussfreiheit einschränken" |
| 5.3 Zeitplanung | FSO Pt 4.2.3, Zif 133-145 | Viertelregel. Interner vs externer Zeitplan. Rückwärtsplanung. Parallelplanung. |
| 5.4.1 Faktorenanalyse | FSO Pt 4.2.4, Zif 146-179 | AUGEZ als taktische Faktoren. AEK-Methode. 3 Führungsstufen-spezifische Faktorengruppen. |
| 5.4.2 Bedrohung | FSO Pt 4.2.4, Zif 180-191 | Lageentwicklungsmöglichkeiten. Bestimmende vs weitere. |
| 5.5.1 Eigene Möglichkeiten | FSO Pt 4.2.5, Zif 192-209 | Varianten: Entwicklung, Präsentation, Analyse (5 Prüfkriterien Zif 206), Bewertung |
| 5.5.2 Entschluss | FSO Pt 4.2.5, Zif 210-216 | Entschluss bestimmt Handeln ALLER Beteiligten. Änderung nur bei 4 Bedingungen (Zif 216). |
| 5.6 Planentwicklung | FSO Pt 4.2.6, Zif 224-241 | Eventualplanung, Unterstützungskonzepte, Aktionsplan |
| 5.7 Befehlsgebung | FSO Pt 4.2.7, Zif 242-245 + Pt 5.7.2-5.7.3 | Endprodukte. Befehlsgebungsrapport. Absicht darlegen. |

### Key Insight: Products Chain

The FSO Chapter 5 (Produkte der Aktionsplanung) shows how products flow between command levels:

```
Übergeordnete Stufe (Bat):
  Planungsvorgabe → Konzept → Plan → Befehl (= INPUT für Kp)
                                         ↓
Eigene Stufe (Kp):                  Befehl Bat
  1. Problemerfassung  ←──────── (lesen, markieren, verstehen)
  2. BdL               ←──────── (Bedrohung ableiten)
  3. Entschlussfassung  ────────→ (Beiträge an Bat liefern)
  4. Planentwicklung    ←──────── (Unterstützungskonzepte)
  5. Befehlsgebung      ────────→ (zur Genehmigung an Bat)
                                         ↓
Unterstellte Stufe (Züge):        Befehl Kp = INPUT für Züge
  ← bekommen ¾ der verfügbaren Zeit (Viertelregel)
```

---

## 2. The 5+2 Workflow in MilAnon

### How the Tool Guides the Commander

Each step of the 5+2 translates into a concrete Claude interaction with defined inputs, questions, and outputs:

### Step 1.1: Initialisierung (4-Farben-Markierung)

**Claude's role:** Do what the Kdt would do with 4 Leuchtstiften — but on the anonymized Bat Bf text.

**Input:** Anonymized Bat Dossier (all documents)
**Doctrine:** BFE 52.080 Kap 5.1.1

**What Claude does:**
```
BLAU markiert: Alles was [EINHEIT_001] direkt betrifft
  → Teile der Absicht und des Auftrags die den eigenen Verband betreffen
  → Erhaltener Auftrag inkl. Eventualplanungen

GRÜN markiert: Was direkt in den Kp Bf übernommen werden kann
  → Nachbartruppen und Partner
  → Textbausteine (Deckname, Kartenmassstab, "Geht an", etc.)

ROT markiert: Bedrohungsrelevante Passagen
  → Bedrohung inkl. Eventualplanungen die den eigenen Verband betreffen

GELB markiert: Besondere Anordnungen
  → Alles unter "Besondere Anordnungen" das [EINHEIT_001] betrifft
```

**Output:** 4 Markdown-Dateien mit den extrahierten Passagen, farbkodiert:
- `01_BLAU_eigener_auftrag.md`
- `02_GRUEN_textbausteine.md`
- `03_ROT_bedrohung.md`
- `04_GELB_beso_anordnungen.md`

Plus: `05_uebersichtskarte.md` — Textuelle Beschreibung der Gesamtlage

### Step 1.2: Problemerfassung

**Claude's role:** Die Problementdeckung, -klärung und -beurteilung durchführen.

**Input:** Ergebnisse aus 1.1
**Doctrine:** BFE 52.080 Kap 5.1.2 + FSO Zif 118-129

**What Claude does:**

**Problementdeckung:**
```
"Worum geht es? Der IST-Zustand ist: [extracted from Bat Bf]
 Der SOLL-Zustand ist: [extracted from Auftrag]
 Die Zeitachse läuft von [Einrücken] bis [Entlassung].
 
 Visualisierung des Gesamtproblems entlang der Zeitachse:
 ──────────────────────────────────────────────────────────→
 |  KVK  | WK Wo 1  | WK Wo 2  | WK Wo 3  | WEMA |
 |  Ausb | Einsatz Phase 1 | Phase 2 | Reorg  |"
```

**Problemklärung — Zerlegung in Teilprobleme:**
```
Problemerfassungs-Matrix:

| Teilproblem | Aufgabenumschreibung | Handlungsrichtlinien | Produkte | Prio | Wer |
|---|---|---|---|---|---|
| TP1: Mob/Einrücken | Mob U gem Bf, Grundbereitschaft | Perm Eigenschutz, OTF Bestand | Vs Bf, Konzept Verladen | 2 | Kdt Stv |
| TP2: KVK-Ausbildung | Standards vermitteln, Rückwärtiges vorbereiten | 72h Kavor | Bf Ausbildung, Lektionspläne | 2 | Kdt |
| TP3: Einsatz | [Hauptauftrag aus Bat Bf] | [Handlungsrichtlinien Bat] | Ei Bf, Beilagen | 1 | Kdt/Zfhr |
| TP4: WEMA/Demob | Abgabe Mat/Fz, Entlassung | Eigenschutz | Wema Konzept | 3 | Kdt |

<!-- KDT ENTSCHEID: Stimmt diese Zerlegung? Fehlen Teilprobleme? Prioritäten korrekt? -->
```

**Problembeurteilung:**
```
Prioritäten nach Eisenhower:
  A-Aufgaben (wichtig+dringend): TP3 Einsatz — sofort selber erledigen
  B-Aufgaben (wichtig+nicht dringend): TP1 Mob, TP2 Ausb — terminieren/delegieren
  C-Aufgaben (nicht wichtig+dringend): [falls vorhanden] — delegieren
  D-Aufgaben (nicht wichtig+nicht dringend): [auf der Seite lassen]
```

**Output:**
- `10_problemerfassung.md` — Problemerfassungs-Matrix
- `11_zeitachse.md` — Visualisierung Gesamtproblem
- Update der Synchronisationsmatrix

### Step 1+: Sofortmassnahmen (OEBAS-VIV)

**Claude's role:** Identifiziere was SOFORT zu tun ist — bevor der Rest der AP weitergeht.

**Input:** Problemerfassung + Bat Bf
**Doctrine:** BFE 52.080 Kap 5.2

**What Claude does:**
```
Sofortmassnahmen (SOMA) — im Gefechtsjournal notieren:

| Datum/Zeit | Was | Wer | Erledigung |
|---|---|---|---|
| Sofort | O: Kdt Stv orientieren über erhaltenen Auftrag | Kdt | |
| Sofort | E: Erkundung Standort [ORT_003] bestellen | Kdt Stv | |
| Sofort | B: Weisungen für Befehlsgebung (Zeitplan Bf-Ausgabe) | Kdt | |
| Sofort | S: Sicherheitskonzept Anreise prüfen | Einh Fw | |
| Sofort | V: Verbindungsaufnahme mit Nachbar-Kp | Kdt | |
| Bis T-14 | V: Logistische Vorausaktionen (Mat-Bestellung bei S4) | Einh Fw | |

Pendenzen (im Notizheft):
- [ ] PISA-Auszug aktualisieren (Bestand prüfen)
- [ ] Kontakt Armeeseelsorger
- [ ] Erkundungsbericht [ORT_003] einholen
- [ ] ...

<!-- KDT ENTSCHEID: Welche SOMA sofort auslösen? Was delegieren? -->
```

**Output:**
- `12_sofortmassnahmen.md` — SOMA-Liste (Gefechtsjournal-Format)
- `13_pendenzen.md` — Pendenzenliste mit Terminen

### Step 1+: Zeitplanung

**Claude's role:** Synchronisationsmatrix erstellen.

**Input:** Bat WAP/Terminliste + eigene Teilprobleme
**Doctrine:** BFE 52.080 Kap 5.3 + FSO Zif 133-145

**What Claude does:**
```
Synchronisationsmatrix:

Viertelregel: Von [Datum Bf-Erhalt] bis [Datum Einsatzbeginn] = X Tage
  → ¼ eigene AP = X/4 Tage
  → ¾ für Unterstellte (Zfhr) = 3X/4 Tage
  → Bf-Ausgabe spätestens am [Datum]

| Phase | Woche | Mo | Di | Mi | Do | Fr | Sa | So |
|---|---|---|---|---|---|---|---|---|
| Interner Zeitplan | KVK | AP | AP | BfAusg | | | | |
| Externer Zeitplan | KVK | Kader-Ausb | Kader-Ausb | Kp Rap | | | | |
| Bat Vorgaben | KVK | URE Bat | | Bf Ger | | | | |
| Unterstellte | KVK | | | | Vorbereitung | Vorbereitung | | |
```

**Output:**
- `14_synchronisationsmatrix.md` — Zeitplan (Markdown-Tabelle)
- `15_viertelregel.md` — Zeitberechnung + Limiten

### Step 2: Beurteilung der Lage (BdL)

**Claude's role:** Durch die AUGEZ-Faktoren führen mit AEK-Methode.

**Input:** Alle Produkte aus Schritt 1 + Bat Bf
**Doctrine:** BFE 52.080 Kap 5.4 + FSO Zif 146-191

**What Claude does — Faktor für Faktor:**

**A — Auftrag:**
```
Aussagen:
  - [EINHEIT_001] soll [Auftrag aus Bat Bf]
  - Im Gesamtrahmen hat [EINHEIT_001] die Rolle [aus Absicht Bat Kdt ableiten]
  - Handlungsspielraum: [frei in X, gebunden in Y]
  - Unterstützung durch: [Nachbar-Kp, Ustü Kp, Art, Genie, etc.]

Erkenntnisse:
  - Die erwartete Leistung ist [minimal/maximal: ...]
  - [EINHEIT_001] kann [X] selbständig, braucht aber für [Y] Unterstützung von [Z]

Konsequenzen BLAU:
  → Schwergewicht auf [Teilauftrag X] legen
  → Für [Teilauftrag Y] Unterstützung bei [Bat] beantragen
```

**U — Umwelt:**
```
Aussagen:
  - Geländekammerung: [aus Karte/Erkundung]
  - Fahrbare Strassen: [aus Karte]
  - Hindernisse: [Gewässer, Engnisse]
  - Dominierende Höhen: [aus Karte]
  - Witterung: [Jahreszeit, Prognose]
  - Zivilbevölkerung: [Verhalten, Dichte]
  - Militärische Infrastruktur: [Trp Stao, KI]

Erkenntnisse (vernetzt mit anderen Faktoren):
  - "Aufgrund des Geländes [U] UND der gegnerischen Reichweiten [G]
     liegen Feuerstellungen auf der westlichen Seite"
  - "Der Fluss teilt meinen Raum in 2 Kammern [U], aber ich muss in
     beiden kämpfen [A] → dezentrale Reserven nötig [E]"

Konsequenzen BLAU:
  → Schlüsselgelände BLAU: [Höhe X, Kreuzung Y]
  → Passage obligé bei [Koordinaten]
```

**G — Gegnerische Mittel:**
```
Aussagen:
  - Absicht/Motivation der Akteure: [aus Bat Bf Bedrohung]
  - Mittel: [Anzahl, Systeme, Reichweiten]
  - Einsatzverfahren: [aus TF/Ei Verf]

Erkenntnisse:
  - Schlüsselbereiche ROT: [gegnerische Stärken/Ansatzpunkte]

Konsequenzen ROT → Konsequenzen BLAU ("Aus ROT mach BLAU"):
  ROT: Gegner kann mit [X] den Raum [Y] aufklären
  BLAU: → Tarnung und Täuschung im Raum [Y] verstärken
```

**E — Eigene Mittel:**
```
Aussagen:
  - Bestand: [aus PISA/Personalplanung]
  - Waffen/Systeme: [Stgw, Mw, Mg, Pzfst — Reichweiten]
  - Einsatzverfahren: [aus Ei Verf Inf Kp]

Erkenntnisse:
  - Schlüsselbereiche BLAU: [eigene Stärken/Systeme]
  - Reichweiten vs Gelände: [wo können wir wirken, wo nicht]
```

**Z — Zeitverhältnisse:**
```
Aussagen:
  - Lageveränderung in [Zeitspanne]: [wahrscheinlich/möglich]
  - Eigene Kräfte einsatzbereit in: [X Stunden nach Alarm]
  - Gegner kann in [Y Stunden] [Z] erreichen

Konsequenzen:
  → Zeitfenster für Einsatzvorbereitung: [X Tage]
  → Bereitschaftsgrad: MBG [1-4]
```

**Vernetzung (Pentagramm) — Das Herzstück:**
```
Jeder Faktor wird mit JEDEM anderen in Beziehung gesetzt:
  A↔U: Auftrag im Kontext des Geländes → wo erfülle ich den Auftrag?
  A↔G: Auftrag vs Gegner → was hindert mich an der Auftragserfüllung?
  A↔E: Auftrag vs eigene Mittel → reichen meine Mittel?
  A↔Z: Auftrag vs Zeit → schaffe ich es rechtzeitig?
  U↔G: Gelände vs Gegner → wo nutzt der Gegner das Gelände?
  U↔E: Gelände vs eigene Mittel → wo kann ich meine Waffen einsetzen?
  U↔Z: Gelände vs Zeit → Witterungseinfluss auf Zeitplan?
  G↔E: Gegner vs Eigene → Kräfteverhältnis?
  G↔Z: Gegner vs Zeit → wann wird der Gegner aktiv?
  E↔Z: Eigene vs Zeit → wann bin ich einsatzbereit?
```

**Output:**
- `20_bdl_augez_analyse.md` — Komplette Faktorenanalyse mit AEK
- `21_schlüsselbereiche.md` — ROT + BLAU Schlüsselbereiche
- `22_konsequenzen_rot.md` — Alle Konsequenzen ROT
- `23_konsequenzen_blau.md` — Alle Konsequenzen BLAU (Grundlage für Varianten)
- `24_bedrohung.md` — Bestimmende + weitere Lageentwicklungsmöglichkeiten

### Step 3: Entschlussfassung

**Claude's role:** Varianten generieren, prüfen, bewerten — Entschluss vorschlagen.

**Input:** Konsequenzen BLAU + Lageentwicklungsmöglichkeiten
**Doctrine:** BFE 52.080 Kap 5.5 + FSO Zif 192-216 + TF 50.030 Kap 5.2

**What Claude does:**

**Varianten generieren:**
```
Variante "BURGWALL":
  Schwergewicht: Links (Raum [ORT_X])
  Organisation: 2 Züge vorne, 1 Zug Reserve rechts
  Reserve: Einsatz bei Durchbruch rechts oder Gegenangriff

Variante "HAMMER":
  Schwergewicht: Zentral (Passage obligé [Koordinaten])
  Organisation: 1 Zug sperrt, 1 Zug Feuerkampf, 1 Zug Reserve
  Reserve: Verstärkung Sperre oder Gegenangriff

Variante "PFEIL":
  Schwergewicht: Rechts (dominierendes Gelände [Höhe X])
  Organisation: Alle 3 Züge gestaffelt, keine dedizierte Reserve
  Reserve: Rückzug auf Ausweichstellung
```

**Variantenprüfung (FSO Zif 206):**
```
| Kriterium | BURGWALL | HAMMER | PFEIL |
|---|---|---|---|
| Angemessen? (Absicht Bat Kdt) | ✅ | ✅ | ⚠️ Passt nur teilweise |
| Exklusiv? (ROS unterschiedlich) | ✅ | ✅ | ✅ |
| Machbar? (Kräfte ausreichend) | ✅ | ✅ | ⚠️ Keine Reserve |
| Tragbar? (Risiken akzeptabel) | ✅ | ⚠️ Eng am Passage | ❌ Kein Rückfallraum |
| Vollständig? (wann/wer/was/wo/wie) | ✅ | ✅ | ⚠️ Reserve fehlt |
```

**Bewertung nach Einsatzgrundsätzen (TF 50.030 Kap 5.2.1):**
```
| Grundsatz | BURGWALL | HAMMER |
|---|---|---|
| Ausrichten auf Ziel | ++ | +++ |
| Schwergewichtsbildung | ++ | +++ |
| Einfachheit | +++ | ++ |
| Sicherheit | +++ | ++ |
| Ökonomie der Kräfte | ++ | ++ |
| Einheitlichkeit des Handelns | +++ | ++ |
| Flexibilität | ++ | + |
| Freiheit des Handelns | ++ | ++ |
| Überraschung | + | ++ |
| Verhältnismässigkeit | +++ | +++ |

Empfehlung: Variante "BURGWALL" — stärkstes Gesamtprofil
<!-- KDT ENTSCHEID: Welche Variante wählst du? Begründung? -->
```

**Entschluss → Absicht → Aufträge:**
```
Entschluss: Variante "BURGWALL" — Schwerpunkt links

Absicht:
"Ich will
  in einer ersten Phase mit [Z1] den Raum [ORT_X] sperren und
    mit [Z2] [Auftrag] sicherstellen;
  in einer zweiten Phase mit [Z3] als Reserve bereithalten,
    auf Befehl Kp Kdt [Reserveeinsatz];
  über alle Phasen den Wachtdienst gem Beilage betreiben."

Aufträge:
  Z1 (+Mw Gr aus Ustü Kp): Sperrt den Raum [ORT_X]
  Z2: Sichert [ORT_Y] und stellt [Auftrag] sicher
  Z3 (Reserve): Hält sich im MBG II bereit für [Reserveeinsätze]
  Kdo Zug: Erstellt und betreibt mob KP

<!-- KDT ENTSCHEID: Absicht und Aufträge bestätigen/anpassen -->
```

**Output:**
- `30_varianten.md` — 2-3 Varianten mit grafischer Darstellung
- `31_variantenpruefung.md` — FSO Zif 206 Prüfung + Einsatzgrundsätze
- `32_entschluss.md` — Gewählte Variante + Begründung
- `33_absicht_auftraege.md` — Absicht + Aufträge (Entwurf für Kdt)

### Step 4: Planentwicklung

**Claude's role:** Besondere Anordnungen und Beilagen ausarbeiten.

**Input:** Entschluss + Bat Bf Beso Anordnungen
**Doctrine:** BFE 52.080 Kap 5.6 + FSO Zif 224-241

**What Claude does:**
```
Besondere Anordnungen:
  - Recht/ROE/ROB: [aus Bat Bf + Taschenkarte]
  - Nachrichtendienst: [BNB aus eigener BdL ableiten]
  - Einsatz:
    - Raumordnung [aus Entschluss]
    - Hindernisführung [aus BdL Konsequenzen]
    - ABC [aus Bat Bf]
  - Logistik:
    - Ns/Rs-Konzept [aus Bat Log Bf + eigene Organisation]
    - Sanitätsdienst [Evakuierungskette]
    - Vpf [aus Bat Dienstbetrieb]
    - V+T [Fahrzeuge, Konvoy-Regeln]
  - Führungsunterstützung:
    - Verbindungen [ANP, Funknetze]
    - Standorte KP

Eventualplanungen:
  - Für "weitere Lageentwicklungsmöglichkeit 1": [Reserveeinsatz A]
  - Für "minimale Auftragserfüllung" (Z1 fällt aus): [Reserveeinsatz B]
  - Für "maximale Auftragserfüllung" (alle erfolgreich): [Chance nutzen C]

Synchronisationsmatrix (final):
  [Alle Phasen, Sequenzen, Kräfte/Mittel zeitlich synchronisiert]
```

**Output:**
- `40_beso_anordnungen.md` — Alle besonderen Anordnungen
- `41_eventualplanung.md` — Vorbehaltene Entschlüsse
- `42_synchronisationsmatrix_final.md`
- `43_beilagen/` — Ordner mit allen Beilagen-Entwürfen

### Step 5: Befehlsgebung (5-Punkte-Befehl)

**Claude's role:** Alles zusammensetzen — der finale Befehl.

**Input:** ALLE Produkte aus Schritten 1-4
**Doctrine:** BFE 52.080 Kap 5.7 + FSO Zif 242-245

**What Claude does:**
```
Zusammensetzung des 5-Punkte-Befehls:

Punkt 1 — Orientierung:
  1.1 Bedrohung          ← aus Step 2 (24_bedrohung.md)
    1.1.1 Bestimmende Lageentwicklungsmöglichkeit
    1.1.2 Weitere Lageentwicklungsmöglichkeiten
    1.1.3 In allen Fällen
  1.2 Erhaltener Auftrag ← aus Step 1.1 (01_BLAU_eigener_auftrag.md)
  1.3 Nachbartruppen     ← aus Step 1.1 (02_GRUEN_textbausteine.md)

Punkt 2 — Absicht       ← aus Step 3 (33_absicht_auftraege.md)

Punkt 3 — Aufträge      ← aus Step 3 (33_absicht_auftraege.md)

Punkt 4 — Beso Anordnungen ← aus Step 4 (40-43)
  + Beilagen:
    1. Lageentwicklungsmöglichkeiten
    2. Abschnittsgrenzen
    3. Führungsraster
    4. Einsatzunterstützung
    5. Pocket Card ROE/ROB
    6. Leistungskatalog
    7. Synchronisationsmatrix
    8. Adressnetzplan
    9. Ausbildung

Punkt 5 — Standorte     ← aus Step 4

Geht an / z K an
```

**Output:**
- `50_einsatzbefehl_einheit.md` — Der komplette 5-Punkte-Befehl
- `51_beilagen/` — Alle referenzierten Beilagen
- `52_befehlsgebung_checkliste.md` — Was in welcher Reihenfolge präsentieren

---

## 3. The Universal Application

The 5+2 applies to EVERYTHING the Kdt does. The only difference is the depth and which doctrine chapters are used:

| Aufgabe | 5+2 Tiefe | Haupt-Doktrin | Endprodukt |
|---|---|---|---|
| Kp Dossier (WK) | Voller 5+2, alle Schritte | BFE 52.080 + 52.081 | Allgemeiner Bf + 15 Beilagen |
| Einsatzbefehl | Voller 5+2, taktischer Fokus | BFE + TF + Ei Verf | Ei Bf Einh (Dok 500) |
| Wachtdienstbefehl | 5+2 mit Sicherungsfokus | WAT 51.301 + BFE | Wachtdienstbefehl (Dok 300) |
| Ausbildungsplanung | Abgekürzter 5+2 | BFE 52.081 Kap 3-4 | Bf Ausbildung (Dok 200) |
| Personalfall (TDL) | Mini-5+2 (PE→BdL→Entschluss) | BFE 52.081 Kap 2 | Zusage/Absage + Marschbefehl |
| Rapport-Vorbereitung | Lageverfolgung → Einsatzbericht | BFE 52.080 Kap 4 | Frontrapport-Input |
| Taktisches Problem | Voller 5+2 Schritt 2+3 | TF 50.030 Kap 5 | BdL + Entschluss |

---

## 4. Implementation Architecture

### Pack Builder with --workflow 5+2

```bash
# Full 5+2 — guided through ALL steps
milanon pack --workflow 5+2 --input anon/ --unit "Inf Kp 56/1" --step 1
# → Produces: Initialisierung + Problemerfassung + SOMA + Zeitplan
# → User reviews, makes KDT ENTSCHEID decisions
# → User pastes Claude's output back

milanon pack --workflow 5+2 --input anon/ --unit "Inf Kp 56/1" --step 2
# → Produces: BdL (AUGEZ + AEK + Konsequenzen)
# → Input includes previous step's output (round-trip)

milanon pack --workflow 5+2 --input anon/ --unit "Inf Kp 56/1" --step 3
# → Produces: Varianten + Prüfung + Entschluss

milanon pack --workflow 5+2 --input anon/ --unit "Inf Kp 56/1" --step 4
# → Produces: Planentwicklung + Beso Anordnungen

milanon pack --workflow 5+2 --input anon/ --unit "Inf Kp 56/1" --step 5
# → Produces: 5-Punkte-Befehl assembled from all products

# Or: All at once (for experienced Kdt or simple problems)
milanon pack --workflow 5+2 --input anon/ --unit "Inf Kp 56/1" --all
```

### System Prompt Architecture (5 Layers)

```
Layer 1 — ROLLE (static, same for all)
  "Du bist der Stabsassistent eines Schweizer Einheitskommandanten (Stufe Kp).
   Du arbeitest IMMER nach dem 5+2 Aktionsplanungsprozess (BFE 52.080 Kap 5).
   Der Kdt arbeitet allein — du bist sein digitaler Stab.
   
   Du kennst:
   - Den Führungsprozess: Lageverfolgung ↔ Aktionsplanung
   - Die 5+2 Führungstätigkeiten und ihre Produkte
   - Die AEK-Methode (Aussage → Erkenntnis → Konsequenz)
   - Die AUGEZ-Faktoren und ihre Vernetzung (Pentagramm)
   - Die Einsatzgrundsätze (TF 17)
   - Die Viertelregel für die Zeitplanung
   - OEBAS-VIV für Sofortmassnahmen
   
   Du denkst immer 1 Stufe hoch (Bat) und 2 Stufen tief (Gruppe).
   Die Schweizer Armee verteidigt — Panzerabwehr ist immer relevant."

Layer 2 — EINHEITS-KONTEXT (generated by milanon context)
  "Deine Einheit: [EINHEIT_001] = Inf Kp 56/1
   Bat: Inf Bat 56 → Ter Div 2 → Kdo Op
   Schwestern: Stabskp 56, Kp 56/2, 56/3, Ustü Kp 56/4
   Stärke: [aus PISA]
   Bestand Schlüsselfunktionen: [Kdt, Stv, Fw, Four, 3 Zfhr]"

Layer 3 — DOKTRIN (workflow-specific chapter extracts)
  [BFE Kap 5.1-5.2 for Step 1]
  [BFE Kap 5.4 + TF Kap 5.2 for Step 2]
  [BFE Kap 5.5 + FSO Zif 206 for Step 3]
  [BFE Kap 5.6-5.7 for Step 4-5]

Layer 4 — AUFGABE (step-specific instructions)
  "Du bist jetzt in Schritt 2: Beurteilung der Lage.
   Führe den Kdt durch die AUGEZ-Faktoren mit AEK-Methode.
   Produziere: AUGEZ-Analyse, Schlüsselbereiche, Konsequenzen ROT/BLAU.
   Markiere Stellen wo der Kdt entscheiden muss mit <!-- KDT ENTSCHEID -->."

Layer 5 — REGELN (static, same for all)
  "- Preserve ALL [PLACEHOLDER] tokens exactly
   - Mark decisions with <!-- KDT ENTSCHEID: ... -->
   - Use Obsidian wiki-links [[PLACEHOLDER]]
   - Flag open questions at the end
   - Reference doctrine sources (BFE Kap X, FSO Zif Y)
   - Separate each output document with --- on its own line
   - Include document filename as # header (e.g. # 20_bdl_augez_analyse.md)"
```

### Claude Project Setup (for other Kdt)

```
project/
  SYSTEM_PROMPT.md        # Layers 1+2+5 combined
  knowledge/
    CONTEXT.md            # Layer 2 (unit-specific)
    bfe_kap5_aktionsplanung.md  # Complete BFE Chapter 5
    fso_kap4_aktionsplanung.md  # FSO Chapter 4.2
    tf_kap5_taktik.md           # TF Chapter 5 (Einsatzgrundsätze)
    wat_wachtdienst.md          # WAT key chapters
    ei_verf_inf_kp.md           # Einsatzverfahren eigene Stufe
    skeletons.md                # All document structure templates
  INSTRUCTIONS.md         # "Sage: 'Starte den 5+2 für meinen WK'"
  WORKFLOWS.md            # Available commands per step
```

---

## 5. What Makes This Different

### vs "Just asking Claude to write a Befehl"

| Aspect | Plain Claude | MilAnon 5+2 Assistent |
|---|---|---|
| Process | Ad-hoc, unstructured | BFE-konformer 5+2 Prozess |
| Intermediate products | None | 15+ Zwischenprodukte (PE, SOMA, BdL, Varianten...) |
| Decision support | Claude decides everything | Claude proposes, Kdt decides (<!-- KDT ENTSCHEID -->) |
| Doctrine conformity | Random | Guaranteed (chapter references in every output) |
| Traceability | None | Every statement traceable to Bat Bf or doctrine |
| Learning effect | None | Kdt learns the 5+2 by doing it |
| Varianten | Claude picks one | 2-3 Varianten with FSO Zif 206 Prüfung |
| Completeness | Depends on prompt | Enforced by process (nothing skipped) |
| Security | Classified data in cloud | Anonymized — no PII leaves the machine |

### vs ChatGPT Custom GPT (the competitor in the Bat)

| Aspect | ChatGPT GPT | MilAnon 5+2 |
|---|---|---|
| Data security | ❌ Data in OpenAI cloud | ✅ Local anonymization |
| Doctrine depth | Surface-level | Full BFE/FSO/TF/WAT integrated |
| Swiss Army specifics | Generic military | Swiss-specific (AUGEZ, Viertelregel, WAT) |
| Unit awareness | None | Full hierarchy (Kdo Op → Div → Bat → Kp → Z) |
| Round-trip | Not possible | Built-in (re-anonymize → update → de-anonymize) |
| Shareable | Per-user | Open Source Starter Kits |
| Process guidance | Template-filling | True 5+2 process guidance with all products |

---

## → Continue: [Part 2 — TF 17 Tactical Knowledge Base](PRODUCT_DESIGN_TF17_APPENDIX.md)

The TF 17 Appendix contains:
- **6.1** Einsatzgrundsätze — The 10-criteria evaluation framework for variants
- **6.2** Taktische Grundsätze — Attack, Defense, Security principles
- **6.3** Führung auf taktischer Stufe — 5 leadership domains
- **6.4** Raumordnung — Spatial vocabulary (Einsatzraum, Feuerraum, etc.)
- **6.5** Taktische Aufgaben — The official verbs for Absicht and Aufträge
- **6.6** Auftragstaktik — WAS, nicht WIE
- **7.** Updated System Prompt Layer 1 with full TF 17 integration
