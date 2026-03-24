# Swiss Military Ranks — Complete Reference

> Source: Official Swiss Army rank insignia chart
> Used by: MilitaryRecognizer (Step 5b) for rank detection

## Enlisted & NCO Ranks (Mannschaft & Unteroffiziere)

| Rank (German) | Abbreviation | Category |
|---------------|-------------|----------|
| Soldat | Sdt | Mannschaft |
| Gefreiter | Gfr | Mannschaft |
| Obergefreiter | Obgfr | Mannschaft |
| Korporal | Kpl | Unteroffizier |
| Wachtmeister | Wm | Unteroffizier |
| Oberwachtmeister | Obwm | Höherer Unteroffizier |
| Fourier | Four | Höherer Unteroffizier |
| Feldweibel | Fw | Höherer Unteroffizier |
| Hauptfeldweibel | Hptfw | Höherer Unteroffizier |
| Adjutant Unteroffizier | Adj Uof | Höherer Unteroffizier |
| Stabsadjutant | Stabsadj | Höherer Unteroffizier |
| Hauptadjutant | Hptadj | Höherer Unteroffizier |
| Chefadjutant | Chefadj | Höherer Unteroffizier |

## Officer Ranks (Offiziere)

| Rank (German) | Abbreviation | Category |
|---------------|-------------|----------|
| Leutnant | Lt | Subalternoffizier |
| Oberleutnant | Oblt | Subalternoffizier |
| Hauptmann | Hptm | Hauptmann |
| Major | Maj | Stabsoffizier |
| Oberstleutnant | Oberstlt | Stabsoffizier |
| Oberst | Oberst | Stabsoffizier |
| Brigadier | Br | Höherer Stabsoffizier |
| Divisionär | Div | Höherer Stabsoffizier |
| Korpskommandant | KKdt | Höherer Stabsoffizier |
| General | General | Höchster Rang |

## Special Officer Designations

| Designation | Abbreviation | Notes |
|-------------|-------------|-------|
| Fachoffizier | Fachof | Specialist officer, equivalent to Hauptmann |
| Generalstabsoffizier | Gst Of | General staff officer |
| Höherer Stabsoffizier | HSO | Senior staff officer |

## Rank Modifiers

| Modifier | Abbreviation | Usage |
|----------|-------------|-------|
| im Generalstab | i Gst | Precedes rank, e.g. "Oberstlt i Gst" |

## Compound Rank Patterns (for regex)

Multi-word ranks that must be detected as ONE entity:
- `Oberstlt i Gst` (3 tokens)
- `Adj Uof` (2 tokens)
- `Fachof (Hptm)` (with parenthetical equivalent)

## Troop Types / Branch Designations (Truppengattungen)

| Branch (German) | Abbreviation |
|-----------------|-------------|
| Infanterie | Inf |
| Panzertruppen | Pz |
| Artillerie | Art |
| Fliegertruppen | Fl |
| Fliegerabwehrtruppen | Flab |
| Genietruppen | G |
| Übermittlungstruppen / Führungsunterstützung | Uem/FU |
| Rettungstruppen | Rttg |
| Logistiktruppen | Log |
| Sanitätstruppen | San |
| Militärische Sicherheit | Mil Sich |
| ABC Abwehrtruppen | ABC Abw |
| Militärischer Nachrichtendienst | Mil ND |
| Militärjustiz | MJ |
| Armeeseelsorge | AS |
| Territorialdienst | Ter D |
| Bereitschaftsdienst | Ber D |
| Rotkreuzdienst | RKD |
| Sport | Sport |
| Militärspiel | Militärspiel |

## Unit Designation Patterns

Common patterns for unit names (regex-detectable):
- `{Branch} Bat {Nr}` — e.g. "Inf Bat 56"
- `{Branch} Kp {Nr}/{Sub}` — e.g. "Inf Kp 56/1"
- `{Branch} Stabskp {Nr}` — e.g. "Inf Stabskp 56"
- `{Branch} Ustü Kp {Nr}` — e.g. "Inf Ustü Kp 56"
- `Ter Div {Nr}` — e.g. "Ter Div 2"
- `Stab {Unit}` — e.g. "Stab Br 1"
- `San Kp {Nr}` — e.g. "San Kp 1"

## Function Designations (Funktionen)

| Function | Abbreviation | Notes |
|----------|-------------|-------|
| Kommandant | Kdt | Commander |
| Kommandant Stellvertreter | Kdt Stv | Deputy commander |
| Zugführer | Zfhr | Platoon leader |
| Gruppenführer | Grfhr | Section leader |
| Einheitskommandant | Einh Kdt | Unit commander |
| Bataillonskommandant | Bat Kdt | Battalion commander |
| Kompanie Kommandant | Kp Kdt | Company commander |
| Einheitsfeldweibel | Einh Fw | Unit sergeant major |
| Einheitsfourier | Einh Four | Unit quartermaster NCO |
