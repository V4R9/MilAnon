# Document Skeletons — Architecture

## The Key Insight

A 5-Punkte-Befehl is a 5-Punkte-Befehl — whether ADF or Berrm.
The STRUCTURE is identical. Only the CONTENT changes per mode.

## Active Skeletons

| Skeleton | Purpose | Modes |
|---|---|---|
| **`5_punkte_befehl_universal.md`** | PRIMARY — Any 5-Punkte-Befehl on Stufe Einheit | ADF + Berrm |
| `000_allgemeiner_befehl.md` | WK-wide administrative order (not purely tactical) | Both |
| `300_wachtdienstbefehl.md` | WAT 51.301 structure (different from 5-Punkte) | Both |

## Superseded (kept as reference)

| Skeleton | Replaced by |
|---|---|
| `500_einsatzbefehl.md` | `5_punkte_befehl_universal.md` with mode markers |
| `500_einsatzbefehl_berrm.md` | `5_punkte_befehl_universal.md` with mode markers |

## How Mode Markers Work

The universal skeleton uses HTML comments as mode markers:
```
<!-- ADF: Text only shown in ADF mode -->
<!-- BERRM: Text only shown in Berrm mode -->
<!-- BOTH: Text shown in both modes -->
<!-- KDT ENTSCHEID: Commander must decide here -->
<!-- FILL: Claude fills from Bat Bf or BdL products -->
```

The Pack builder strips irrelevant mode markers before including the skeleton in the prompt.

## DOCX Style Mapping

The CH Armee Befehl Vorlage defines these Word styles:

| Markdown | DOCX Style | Usage |
|---|---|---|
| `# Heading` | `Heading 1` | "Grundlagen" header |
| `## Title` | `Subject heading` | Deckname (bold, 13pt) |
| `### 1 Title` | `1. Main title` | Hauptpunkte 1-5 |
| `#### 1.1 Title` | `1.1 Title` | Unterpunkte |
| `##### 1.1.1 Title` | `1.1.1 Title` | Sub-Unterpunkte |
| Paragraph text | `Text Indent` | Fliesstext |
| `- Bullet` | `Bullet List 1` | Aufzählungen |
| `| Table |` | Table | Aufträge, Standorte |

The DOCX export (E17) must use these exact styles to match the official Armee-Vorlage.
Source: `Unterlagen Review Product Design/Vorlagen CH Armee/Befehl Vorlage .docx`
