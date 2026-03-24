# Cheat Sheet — 5+2 mit Claude

> Drucke dieses Blatt aus oder leg es neben deinen Laptop.
> Du brauchst es nur, um zu wissen was du Claude als nächstes sagen sollst.

---

## Vorbereitung (einmalig, auf deinem Mac)

```
milanon project generate --unit "Inf Kp 56/1" --input bat_dossier.pdf --output ~/claude_project/
```

Dann in Claude.ai:
1. Neues Projekt erstellen
2. SYSTEM_PROMPT.md als "Project Instructions" pasten
3. Alle Files aus `knowledge/` als Knowledge hochladen
4. Neuen Chat starten

---

## Schritt 1 — Problemerfassung

**Sage zu Claude:**
> Analysiere das Bat Dossier für meine Einheit. Führe die Initialisierung mit 4-Farben-Markierung durch und erstelle die Problemerfassung mit Teilproblemen, SOMA und Zeitplan.

**Claude produziert:**
- 4-Farben-Markierung (BLAU/GRÜN/ROT/GELB)
- Problemerfassungs-Matrix (Teilprobleme mit Prio)
- Sofortmassnahmen (OEBAS-VIV)
- Synchronisationsmatrix

**Du entscheidest:**
- Stimmt die Priorisierung der Teilprobleme?
- Fehlen Sofortmassnahmen?
- Sage Claude was angepasst werden muss.

**Wenn zufrieden:** "Passt. Weiter mit der Beurteilung der Lage."

---

## Schritt 2 — Beurteilung der Lage (BdL)

**Sage zu Claude:**
> Führe die Beurteilung der Lage durch. Analysiere alle AUGEZ-Faktoren mit der AEK-Methode.

**Claude produziert:**
- AUGEZ-Analyse (Auftrag, Umwelt, Gegner, Eigene Mittel, Zeit)
- Für jeden Faktor: Aussage → Erkenntnis → Konsequenz
- Bedrohungsmatrix
- Konsequenzen für eigenen Einsatz

**Du entscheidest:**
- Stimmen die Konsequenzen?
- Wo liegt das Schwergewicht? (Gelände? Zeit? Kräfte?)
- Welche Bedrohung ist bestimmend?

**Wenn zufrieden:** "Passt. Erstelle Varianten für den Entschluss."

---

## Schritt 3 — Entschlussfassung

**Sage zu Claude:**
> Erstelle 2-3 Einsatzvarianten. Bewerte sie anhand der 10 Einsatzgrundsätze und empfiehl eine Variante.

**Claude produziert:**
- 2-3 Varianten (ROS: Raum, Operation, Stärke)
- Bewertung jeder Variante gegen die 10 Einsatzgrundsätze
- Empfehlung mit Begründung
- Absicht und Aufträge basierend auf der gewählten Variante

**Du entscheidest:**
- Welche Variante? (Claude empfiehlt, DU entscheidest!)
- Stimmt die Absicht?
- Stimmen die Aufträge pro Zug?
- Auftragstaktik: Steht nur WAS, nicht WIE?

**Wenn zufrieden:** "Variante 2 mit folgender Anpassung: [deine Änderung]. Entwickle den Plan."

---

## Schritt 4 — Planentwicklung

**Sage zu Claude:**
> Entwickle den Plan: Besondere Anordnungen, Beilagen, Nachschub, Sanitätsdienst, FU-Ordnung. Berücksichtige die Vorgaben aus dem Bat Dossier.

**Claude produziert:**
- Besondere Anordnungen (Punkt 4 des Befehls)
- Nachschub und Versorgung
- Sanitätsdienst
- FU-Ordnung
- Eventualplanungen

**Du entscheidest:**
- Stimmen die Log-Anordnungen?
- Sind die Standorte realistisch?
- Fehlen Beilagen?

**Wenn zufrieden:** "Passt. Schreibe den vollständigen Einsatzbefehl."

---

## Schritt 5 — Befehlsgebung

**Sage zu Claude:**
> Erstelle den vollständigen 5-Punkte-Einsatzbefehl. Verwende das Skeleton aus den Knowledge Files. Stelle sicher, dass alle Platzhalter [EINHEIT_xxx], [ORT_xxx] etc. erhalten bleiben.

**Claude produziert:**
- Vollständiger 5-Punkte-Befehl:
  1. Orientierung (Bedrohung, Erhaltener Auftrag, Nachbarn)
  2. Absicht
  3. Aufträge (Tabelle pro Zug)
  4. Besondere Anordnungen
  5. Standorte
- Beilagen + Verteiler

**Du prüfst:**
- Ist der Befehl vollständig? (Alle 5 Punkte?)
- Stimmen die Aufträge mit deinem Entschluss überein?
- Sind alle Platzhalter [xxx] noch da? (Wichtig für De-Anonymisierung!)

**Wenn zufrieden:** Den ganzen Befehl kopieren.

---

## Abschluss (auf deinem Mac)

```bash
# Claude's Output in dein System bringen:
milanon unpack --clipboard --output vault/Dossier/ --split

# Word-Dokument mit echten Namen erstellen:
milanon export vault/Dossier/ei_bf.md --docx --deanonymize --output befehl_inf_kp_56_1.docx

# Fertig! Öffne das Word-Dokument:
open befehl_inf_kp_56_1.docx
```

---

## Weitere Befehle für Claude

| Was du brauchst | Sage zu Claude |
|---|---|
| Wachtdienstbefehl | "Erstelle den Wachtdienstbefehl gemäss WAT." |
| Eventualplanung Halten | "Erstelle die EP Halten Standort." |
| Eventualplanung Kampf | "Erstelle die EP Kampf im Interessenraum." |
| Dienstbetrieb | "Erstelle den Ergänzungsbefehl Dienstbetrieb." |
| Ausbildungsbefehl | "Erstelle den Befehl für die Ausbildung." |
| Korrektur | "Ändere in Punkt 3: Z Ambos soll sperren statt halten." |
| Nochmal | "Überarbeite den Befehl basierend auf meinen Rückmeldungen." |

---

## Wichtig zu wissen

- **Claude macht VORSCHLÄGE mit konkreten Optionen, du WÄHLST.**
  - Bei jeder Entscheidung zeigt Claude 2-3 Optionen mit kurzer Begründung
  - Du sagst nur: "Option 2" oder "Option 1, aber mit Anpassung X"
  - Beispiel: Claude fragt "Schwergewicht: (A) Zugang Ost sperren (B) Raum Süd halten (C) Bewegungslinie Nord kontrollieren" → Du sagst "A" Überall wo <!-- KDT ENTSCHEID --> steht, musst DU eine Entscheidung treffen.
- **Platzhalter nicht löschen!** [PERSON_001], [ORT_003] etc. werden am Ende durch echte Namen ersetzt. Wenn du sie löschst, fehlen die Namen im Word-Dokument.
- **Du kannst jederzeit korrigieren.** "Ändere X" funktioniert immer. Claude behält den ganzen Kontext.
- **Ein Chat = ein Dossier.** Mach nicht mehrere Dossiers im gleichen Chat.
