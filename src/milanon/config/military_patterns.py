"""Centralized regex pattern definitions for Swiss military document recognition.

Used by PatternRecognizer (structured PII) and MilitaryRecognizer (domain-specific).
All patterns are compiled once at import time.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Structured PII patterns — used by PatternRecognizer
# ---------------------------------------------------------------------------

# AHV-Nummer: 756.XXXX.XXXX.XX  (Swiss social security number)
AHV_PATTERN: re.Pattern[str] = re.compile(r"\b756\.\d{4}\.\d{4}\.\d{2}\b")

# Swiss phone numbers — three supported formats:
#   +41 79 535 80 46   (international, spaces)
#   079 535 80 46      (local, spaces)
#   0795358046         (compact, no spaces)
PHONE_INTL_PATTERN: re.Pattern[str] = re.compile(
    r"\+41[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b"
)
PHONE_LOCAL_PATTERN: re.Pattern[str] = re.compile(
    r"\b0\d{2}[\s\-]\d{3}[\s\-]\d{2}[\s\-]\d{2}\b"
)
PHONE_COMPACT_PATTERN: re.Pattern[str] = re.compile(r"\b0\d{9}\b")

# Email address (RFC 5321 simplified)
EMAIL_PATTERN: re.Pattern[str] = re.compile(
    r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"
)

# Date of birth: dd.mm.yyyy
GEBURTSDATUM_PATTERN: re.Pattern[str] = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

# Initial + ALLCAPS surname: "D. MUFFLER", "M. KOCH", "L. STORRER"
# Matches organigramm/address-list names that appear without a rank prefix.
INITIAL_SURNAME_PATTERN: re.Pattern[str] = re.compile(
    r"(?<!\w)[A-ZÄÖÜ]\.\s+[A-ZÄÖÜ]{2,}(?:[\-][A-ZÄÖÜ]{2,})*(?!\w)"
)

# Swiss street address: "Bahnhofstr. 42" or "Bahnhofstr. 42, 4058 Basel"
# Requires a street suffix and a house number to avoid false positives.
ADRESSE_PATTERN: re.Pattern[str] = re.compile(
    r"\b[A-ZÄÖÜ][a-zA-ZäöüÄÖÜ\-]*"
    r"(?:str\.|strasse|gasse|weg|allee|platz|rain|matt|feld|halde|berg)"
    r"\s+\d+[a-z]?"
    r"(?:\s*,\s*\d{4}\s+[A-ZÄÖÜ][a-zA-ZäöüÄÖÜ\-]+)?",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Military domain — rank abbreviations (longest-first to avoid partial matches)
# ---------------------------------------------------------------------------

RANK_ABBREVIATIONS: list[str] = [
    "Oberstlt i Gst",  # 3-word rank — must precede "Oberstlt"
    "Adj Uof",         # 2-word rank — must precede "Adj"
    "Adj",             # standalone — must follow "Adj Uof" (longest match first)
    "Chefadj",
    "Stabsadj",
    "Hptadj",
    "General",
    "Oberstlt",
    "Fachof",
    "Hptfw",
    "Obgfr",
    "KKdt",
    "Obwm",
    "Oberst",
    "Hptm",
    "Oblt",
    "Four",
    "Maj",
    "Fw",
    "Kpl",
    "Gfr",
    "Wm",
    "Br",
    "Div",
    "Sdt",
    "Lt",
]

# ---------------------------------------------------------------------------
# Military domain — function abbreviations (longest-first)
# ---------------------------------------------------------------------------

FUNCTION_ABBREVIATIONS: list[str] = [
    "Bat Kdt Stv",
    "Einh Kdt",
    "Einh Fw",
    "Einh Four",
    "Bat Kdt",
    "Kp Kdt",
    "Kdt Stv",
    "Grfhr",
    "Zfhr",
    "Kdt",
]

# ---------------------------------------------------------------------------
# Military domain — branch abbreviations (Truppengattungen)
# ---------------------------------------------------------------------------

BRANCH_ABBREVIATIONS: list[str] = [
    "ABC Abw",
    "Mil Sich",
    "Mil ND",
    "Flab",
    "Rttg",
    "Log",
    "San",
    "Inf",
    "Art",
    "Pz",
    "Fl",
    "MJ",
    "AS",
    "G",
]

# ---------------------------------------------------------------------------
# Compiled unit-designation pattern
# Matches: "Inf Bat 56", "Inf Kp 56/1", "Ter Div 2", "San Kp 1"
# ---------------------------------------------------------------------------

_branch_alt = "|".join(re.escape(b) for b in BRANCH_ABBREVIATIONS)

UNIT_PATTERN: re.Pattern[str] = re.compile(
    r"(?<!\w)(?:" + _branch_alt + r")"
    r"\s+(?:Bat|Kp|Stabskp|Div|Br|Stab(?:skp)?|Ustü\s+Kp)"
    r"\s+\d+(?:/\d+)?"
    r"(?!\w)"
)

# Ter Div N does not use a branch prefix — handle separately
TER_DIV_PATTERN: re.Pattern[str] = re.compile(r"(?<!\w)Ter\s+Div\s+\d+(?!\w)")

# ---------------------------------------------------------------------------
# Compiled rank+name pattern
# Matches: "Hptm Marco BERNASCONI", "Oberstlt i Gst Thomas WEGMÜLLER", "Lt MUSTER"
# Group 1 = rank, Group 2 = name (firstname? LASTNAME)
# ---------------------------------------------------------------------------

_rank_alt = "|".join(re.escape(r) for r in RANK_ABBREVIATIONS)

# First name: optional — title-case word (may contain umlauts, hyphens)
_FIRSTNAME = r"(?:[A-ZÄÖÜ][a-zäöüé][\w\-]*\s+)?"
# Last name: ALL-CAPS, 1–3 words (e.g. BERNASCONI, WEGMÜLLER, DE LA CROIX)
_LASTNAME = r"[A-ZÄÖÜ]{2,}(?:[\s\-][A-ZÄÖÜ]{2,})*"

RANK_NAME_PATTERN: re.Pattern[str] = re.compile(
    r"(?<!\w)(" + _rank_alt + r")\s+(" + _FIRSTNAME + _LASTNAME + r")"
)
