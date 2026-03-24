# PISA 410 Export — Column Mapping Reference

> Standard personnel export from PISA (Personalinformationssystem der Armee).
> This is the "Standardliste 410" available to all company commanders.
> Source: Phase 0 stakeholder input + sample export analysis.

## Column Structure (45 columns)

| # | PISA Column | Entity Type | Notes |
|---|-------------|-------------|-------|
| 1 | Versicherten Nr | `AHV_NR` | Format: `756.XXXX.XXXX.XX` |
| 2 | Einteilung | `EINHEIT` | e.g. "Inf Kp 56/1" |
| 3 | Dienst bei | `EINHEIT` | Usually same as Einteilung |
| 4 | Grad | `GRAD_FUNKTION` | Short form: "Hptm", "Sdt", "Gfr" |
| 5 | i Gst | (modifier for Grad) | "J" or "N" — if "J", prepend "i Gst" to rank |
| 6 | Name | `NACHNAME` | e.g. "Fischer" |
| 7 | Vorname | `VORNAME` | e.g. "Lukas" |
| 8 | Sprache | — | Not anonymized (D/F/I) |
| 9 | NZL Diensttage | — | Not anonymized (number) |
| 10 | Funktion | `FUNKTION` | e.g. "Kdt", "Zfhr", "Grfhr" |
| 11 | Funktionszusatz | `FUNKTION` | Additional function info |
| 12 | Wohnadresse 1 | `ADRESSE` | Street + number |
| 13 | Wohnadresse 2 | `ADRESSE` | Additional address line |
| 14 | Wohnadresse 3 | `ADRESSE` | Additional address line |
| 15 | PLZ Wohnadresse | `ADRESSE` | Postal code |
| 16 | Wohnort | `ORT` | City name |
| 17 | Kanton Wohnadresse | — | Canton abbreviation (part of address context) |
| 18 | Postadresse 1 | `ADRESSE` | Mailing address (if different) |
| 19 | Postadresse 2 | `ADRESSE` | — |
| 20 | Postadresse 3 | `ADRESSE` | — |
| 21 | PLZ Postadresse | `ADRESSE` | — |
| 22 | Wohnort Postadresse | `ORT` | — |
| 23 | Kanton Postadresse | — | — |
| 24 | Telefon Privat | `TELEFON` | — |
| 25 | Telefon Geschäft | `TELEFON` | — |
| 26 | Mobile Privat | `TELEFON` | May have `*` prefix (primary) |
| 27 | Mobile Geschäft | `TELEFON` | — |
| 28 | E-Mail geschäftlich | `EMAIL` | — |
| 29 | E-Mail privat | `EMAIL` | May have `*` prefix (primary) |
| 30 | E-Mail sonst | `EMAIL` | — |
| 31 | Geschlecht | — | Not anonymized (M/F) |
| 32 | Geburtsdatum | `GEBURTSDATUM` | Format: `dd.mm.yyyy` |
| 33 | PSP-Bezeichnung | — | Security clearance level |
| 34 | PSP gültig bis | — | Date |
| 35 | Dienstbemerkung 1 | — | Not anonymized (stakeholder decision: not relevant) |
| 36 | Datum von | — | Date range for remark 1 |
| 37 | Datum bis | — | — |
| 38 | Dienstbemerkung 2 | — | Not anonymized |
| 39 | Datum von | — | — |
| 40 | Datum bis | — | — |
| 41 | Dienstbemerkung 3 | — | Not anonymized |
| 42 | Datum von | — | — |
| 43 | Datum bis | — | — |
| 44 | DIMILAR Status | — | Not anonymized |
| 45 | (empty) | — | Trailing empty column |

## Import Logic

When importing a PISA 410 export, the tool should:

1. Skip row 1 (report title, not data).
2. Use row 2 as column headers.
3. Process data rows (3+).
4. For each row, create entity mappings for:
   - `PERSON` = "{Vorname} {Name}" (combined full name)
   - `NACHNAME` = Name column
   - `VORNAME` = Vorname column
   - `GRAD_FUNKTION` = Grad column (+ "i Gst" if i_gst == "J")
   - `AHV_NR` = Versicherten Nr column
   - `EINHEIT` = Einteilung column
   - `FUNKTION` = Funktion column (+ Funktionszusatz if present)
   - `ADRESSE` = Wohnadresse 1 + PLZ + Wohnort (combined)
   - `ORT` = Wohnort column
   - `TELEFON` = all non-empty phone columns (strip `*` prefix)
   - `EMAIL` = all non-empty email columns (strip `*` prefix)
   - `GEBURTSDATUM` = Geburtsdatum column
5. Strip `*` prefix from phone/email (PISA marks primary contact with `*`).
6. Skip empty values — don't create mappings for blank fields.
7. Create entity aliases for name variants (e.g. "FISCHER" uppercase, "L. Fischer" abbreviated).

## Sample Row

```
756.1234.5678.97 | Inf Kp 56/1 | Hptm | N | Fischer | Lukas | Kdt | Bahnhofstr. 42 | 4058 | Basel | BS | +41 79 555 12 34 | lukas.fischer@example.com | lukas.fischer@milweb.ch | lukas@fischer-consulting.ch | M | 15.03.1995
```
