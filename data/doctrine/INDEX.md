# Doctrine Knowledge Base

> Central Concept: **5+2 Aktionsplanungsprozess** (BFE 52.080 Kap 5)
> See INDEX.yaml for machine-readable workflow → chapter mapping

## The 5+2 at a Glance

```
5 Führungstätigkeiten:                +2 Begleitend:
1. Problemerfassung                   • Sofortmassnahmen (OEBAS-VIV)
2. Beurteilung der Lage (AUGEZ)       • Zeitplanung (Synchronisationsmatrix)
3. Entschlussfassung (Varianten)      (+ Risikomanagement)
4. Planentwicklung
5. Befehlsgebung (5-Punkte-Befehl)
```

Every workflow in MilAnon is a specialized application of this process.

## Available Doctrine Files (11)

| File | Regulation | Size | Key Content |
|---|---|---|---|
| `52_080_bfe_einsatz.md` | BFE 52.080 | 280 KB | **5+2 Prozess**, Aktionsplanung, Befehlsgebung |
| `52_081_bfe_ausbildung.md` | BFE 52.081 | 220 KB | Personal, Ausbildungsplanung, Checklisten |
| `51_301_wachtdienst_aller_truppen.md` | WAT 51.301 | 131 KB | Wachtdienstbefehl, Pflichten, ROE |
| `50_030_taktische_fuehrung.md` | TF 50.030 | 669 KB | Kap 5: Einsatzgrundsätze, Raumordnung, Taktik |
| `50_040_fso_17.md` | FSO 50.040 | 228 KB | Führungsprozesse, Stabsorganisation |
| `50_041_bfa_17.md` | BFA 50.041 | 155 KB | Behelf Führung Armee |
| `53_005_fuehrung_einsatz_inf.md` | 53.005 | 345 KB | Führung und Einsatz der Infanterie |
| `53_005_21_ei_verf_inf_bat.md` | 53.005.21 | 257 KB | Einsatzverfahren Inf Bat (Stufe drüber) |
| `53_005_23_ei_verf_inf_kp.md` | 53.005.23 | 332 KB | Einsatzverfahren Inf Kp (**eigene Stufe**) |
| `53_005_25_ei_verf_inf_z.md` | 53.005.25 | 435 KB | Einsatzverfahren Inf Zug (2 Stufen tiefer) |
| `53_126_feuerkampf_panzerabwehr.md` | 53.126.21 | 3 KB | Panzerabwehr (Verteidigung = Kernauftrag) |

## How to Add a New Regulation

1. Convert to Markdown (or obtain existing .md)
2. Place in `data/doctrine/` with naming convention: `{nummer}_{kurzname}.md`
3. Add entry to `INDEX.yaml` under `doctrine_files` with key chapters
4. Map to relevant workflows in `INDEX.yaml` under `workflows`
5. Create chapter extracts in `data/doctrine/extracts/` for token-efficient prompts

## Directory Structure

```
data/doctrine/
  INDEX.yaml              # Workflow → chapter mapping (machine-readable)
  INDEX.md                # This file (human-readable)
  *.md                    # Full regulation files
  extracts/               # Chapter-level extracts for prompts
    bfe_befehlsschema.md  # BFE Kap 5.3 only
    bfe_fuehrungsprozess.md
    tf_kap5_grundkenntnisse.md
    wat_wachtdienstbefehl.md
    ...
  skeletons/              # Document structure templates
    000_allgemeiner_befehl.md
    300_wachtdienstbefehl.md
    500_einsatzbefehl.md
```
