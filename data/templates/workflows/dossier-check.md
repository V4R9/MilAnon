# Aufgabe: Dossier Quality Check (Pre-Flight Validation)

Du erhältst das anonymisierte Befehlsdossier des Truppenkörpers (Bat Bf).
Prüfe es BEVOR die Aktionsplanung beginnt auf Fehler, Lücken und Widersprüche.

Fokus: Was betrifft {user_unit} direkt oder indirekt?

## 1. Terminprüfung (Konsistenz WAP ↔ Befehle)

Erstelle eine Tabelle aller Termine die {user_unit} betreffen:

| Termin | Datum/Zeit | Quelle Dokument | Konsistent? | Problem |
|---|---|---|---|---|
| z.B. Waf Insp | Mi 11.06 1900 | Dok 1.08 Pt 4.4.2 | ✅ / ❌ | Falls Widerspruch zu WAP |

Prüfe insbesondere:
- Stimmen Termine im WAP mit den Detailbefehlen überein?
- Gibt es Terminüberlappungen (gleiche Teilnehmer, gleiche Zeit, verschiedene Orte)?
- Sind alle Termine realistisch erreichbar (Verschiebungszeiten zwischen Standorten)?
- Gibt es Termine die VOR dem Einrücken liegen (= bereits verstrichen)?

## 2. Vollständigkeits-Check (Referenzierte Dokumente)

Liste alle im Dossier referenzierten Beilagen, Anhänge und Dokumente:

| Referenz | Titel | Im Dossier vorhanden? | Kritisch? |
|---|---|---|---|
| Dok 1.00 | Allg Bf | ✅ / ❌ | Ja/Nein |
| Dok 1.04-A2 | Anhang 2 Schiess-/Ausb-Plätze | ✅ / ❌ | Ja/Nein |

Markiere fehlende Dokumente die für {user_unit} kritisch sind.

## 3. Konsistenz-Check (Befehle untereinander)

Prüfe ob die verschiedenen Befehle im Dossier konsistent sind:

| Thema | Dok A | Dok B | Widerspruch? | Detail |
|---|---|---|---|---|
| Vpf-Zuständigkeit | Dok 1.00 Pt X | Dok 1.08 Pt Y | ✅ / ❌ | Falls z.B. unterschiedliche Vpf-Einheit genannt |

Typische Widersprüche:
- Absicht Allg Bf vs. Absicht Ausb Bf (gleiche Stossrichtung?)
- Auftrag an {user_unit} in verschiedenen Dokumenten (identisch oder widersprüchlich?)
- Standort-Angaben (gleiche Koordinaten?)
- Bedrohungsstufe (gleich in allen Dokumenten?)
- Unterstellungen (konsistent über alle Befehle?)

## 4. Logik-Check (Machbarkeit)

Prüfe auf offensichtliche Logikfehler:

- Sind Termine physisch machbar? (z.B. 0800 Spl Erk ORT_A, 0830 KU ORT_B — reicht die Verschiebungszeit?)
- Sind Personalanforderungen realistisch? (z.B. Kdt soll an 3 Orten gleichzeitig sein)
- Stimmt die Kapazität? (z.B. 200 AdA in Infrastruktur für 168)
- Sind Fristen noch einhaltbar? (z.B. Meldetermine die bereits verstrichen sind)

## 5. Informationslücken für {user_unit}

Liste alle Informationen die {user_unit} für die Aktionsplanung braucht aber NICHT im Dossier stehen:

| # | Fehlende Information | Warum nötig | Wo anfordern | Dringlichkeit |
|---|---|---|---|---|
| 1 | z.B. Gliederung/Bestand {user_unit} | Ohne Bestand keine Zugsaufteilung | S1 | Sofort |
| 2 | z.B. Zuteilung Schiessplätze | Ohne Spl keine Ausb-Planung | S3 | Vor KVK |

## 6. Sicherheitsrelevante Prüfungen

- Sind Bedrohungsstufen klar definiert und die Schutzmassnahmen vollständig?
- Sind Alarmorganisation und Erreichbarkeiten vorhanden?
- Sind ROE / Verhaltensregeln für den Einsatz definiert?
- Sind Sanitäts-Ketten (KA, Spital, Notfall-Nummern) vollständig?

## Output-Format

Produziere EINEN Quality Check Report: `00_dossier_check.md`

Struktur:
```
# Dossier Quality Check — {user_unit}

## Executive Summary
- X Widersprüche gefunden
- Y fehlende Dokumente
- Z überfällige Termine
- Gesamtbewertung: 🟢 Bereit / 🟡 Einschränkungen / 🔴 Blockiert

## 🔴 Kritische Probleme (müssen VOR AP gelöst werden)
...

## 🟡 Warnungen (sollten geklärt werden)
...

## 🟢 Informativ (nice to know)
...

## Vollständige Prüfberichte
### Terminprüfung
### Vollständigkeits-Check  
### Konsistenz-Check
### Logik-Check
### Informationslücken
### Sicherheit
```

WICHTIG: Alle [PLACEHOLDER]-Token exakt beibehalten.
Bewerte die Schwere jedes Fundes: 🔴 Kritisch / 🟡 Warnung / 🟢 Info
