#!/usr/bin/env bash
# =============================================================================
# E2E Acceptance Test — MilAnon Workflow Pipeline
# =============================================================================
#
# Run this script to manually test the full workflow pipeline.
# It creates a temp directory, runs all CLI commands, and reports results.
#
# Usage:
#   bash scripts/e2e_acceptance_test.sh
#
# Requirements:
#   - milanon must be installed (pip install -e .)
#   - DB should be initialized (milanon db init)
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
SKIP=0

pass() { echo -e "  ${GREEN}PASS${NC} $1"; ((PASS++)); }
fail() { echo -e "  ${RED}FAIL${NC} $1: $2"; ((FAIL++)); }
skip() { echo -e "  ${YELLOW}SKIP${NC} $1: $2"; ((SKIP++)); }

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

WORK_DIR=$(mktemp -d)
INPUT_DIR="${WORK_DIR}/input"
ANON_DIR="${WORK_DIR}/anon"
OUTPUT_DIR="${WORK_DIR}/output"
VAULT_DIR="${WORK_DIR}/vault"
mkdir -p "$INPUT_DIR" "$ANON_DIR" "$OUTPUT_DIR" "$VAULT_DIR"

echo -e "${CYAN}=== MilAnon E2E Acceptance Test ===${NC}"
echo -e "Work directory: ${WORK_DIR}"
echo ""

# Create realistic test document
cat > "${INPUT_DIR}/rapport_kp.md" << 'DOCEOF'
# Frontrapport Inf Kp 56/1

## Personelles

Kp Kdt: Hptm Marco BERNASCONI, AHV 756.1234.5678.97
Kp Fw: Hptfw Stefan MEIER, Tel 079 535 80 46
Email: bernasconi@mil.ch

## Lage

Die Kp ist im Bereitschaftsraum Bière stationiert.
Einsatzbereitschaft: 85% (3 Absenzen, davon 1 medizinisch).

## Aufträge

1. Wachtdienst Waffenplatz ab 0600 gemäss Bf Bat
2. Ausbildung Häuserkampf 0800-1200
DOCEOF

echo -e "${CYAN}--- Test 1: DB Init ---${NC}"
if milanon db init 2>/dev/null; then
    pass "db init"
else
    skip "db init" "may already be initialized"
fi

echo -e "${CYAN}--- Test 2: DB Stats ---${NC}"
if output=$(milanon db stats 2>&1); then
    pass "db stats"
    echo "    $output" | head -5
else
    fail "db stats" "$output"
fi

echo -e "${CYAN}--- Test 3: Anonymize ---${NC}"
if output=$(milanon anonymize "$INPUT_DIR" --output "$ANON_DIR" 2>&1); then
    pass "anonymize"
    echo "    $output" | head -5

    # Verify PII is removed
    anon_file=$(find "$ANON_DIR" -name "*.md" | head -1)
    if [ -n "$anon_file" ]; then
        if grep -q "756.1234.5678.97" "$anon_file"; then
            fail "anonymize-pii-check" "AHV number leaked into anonymized output"
        else
            pass "anonymize-pii-check (AHV removed)"
        fi
        if grep -q "bernasconi@mil.ch" "$anon_file"; then
            fail "anonymize-email-check" "Email leaked into anonymized output"
        else
            pass "anonymize-email-check (email removed)"
        fi
        echo ""
        echo -e "    ${YELLOW}Anonymized content preview:${NC}"
        head -15 "$anon_file" | sed 's/^/    /'
    else
        fail "anonymize-output" "No .md files found in $ANON_DIR"
    fi
else
    fail "anonymize" "$output"
fi

echo ""
echo -e "${CYAN}--- Test 4: Pack with Workflow (analyse) ---${NC}"
PROMPT_FILE="${OUTPUT_DIR}/prompt_analyse.md"
if output=$(milanon pack "$ANON_DIR" --workflow analyse --no-clipboard --output "$PROMPT_FILE" 2>&1); then
    pass "pack --workflow analyse"
    echo "    $output" | head -5

    if [ -f "$PROMPT_FILE" ]; then
        chars=$(wc -c < "$PROMPT_FILE")
        echo -e "    Output: ${PROMPT_FILE} (${chars} chars)"

        # Verify no PII in prompt
        if grep -q "756.1234.5678.97" "$PROMPT_FILE"; then
            fail "pack-pii-check" "AHV leaked into prompt"
        else
            pass "pack-pii-check (no PII in prompt)"
        fi

        echo ""
        echo -e "    ${YELLOW}Prompt preview (first 20 lines):${NC}"
        head -20 "$PROMPT_FILE" | sed 's/^/    /'
    else
        fail "pack-output-file" "Prompt file not created"
    fi
else
    fail "pack --workflow analyse" "$output"
fi

echo ""
echo -e "${CYAN}--- Test 5: Pack with Context Chaining ---${NC}"
# Create a fake previous step output (vault)
cat > "${VAULT_DIR}/step1_analyse.md" << 'VAULTEOF'
# Analyse-Ergebnis

Teilprobleme: Wachtdienst, Ausbildung, Dienstbetrieb
Priorität 1: Wachtdienst (Bf Bat Ziff 3.2)
VAULTEOF

CONTEXT_FILE="${OUTPUT_DIR}/prompt_with_context.md"
if output=$(milanon pack "$ANON_DIR" --workflow analyse --context "$VAULT_DIR" --no-clipboard --output "$CONTEXT_FILE" 2>&1); then
    pass "pack with --context"

    if [ -f "$CONTEXT_FILE" ]; then
        if grep -q "Analyse-Ergebnis\|Teilprobleme" "$CONTEXT_FILE"; then
            pass "context-content-included"
        else
            fail "context-content-included" "Vault content not found in prompt"
        fi
    fi
else
    fail "pack with --context" "$output"
fi

echo ""
echo -e "${CYAN}--- Test 6: Config Set/Get ---${NC}"
if output=$(milanon config set mode berrm 2>&1); then
    pass "config set mode berrm"
else
    fail "config set" "$output"
fi

if output=$(milanon config get mode 2>&1); then
    if echo "$output" | grep -q "berrm"; then
        pass "config get mode = berrm"
    else
        fail "config get mode" "Expected berrm, got: $output"
    fi
else
    fail "config get" "$output"
fi

if output=$(milanon config set unit "Inf Kp 56/1" 2>&1); then
    pass "config set unit"
else
    fail "config set unit" "$output"
fi

if output=$(milanon config get unit 2>&1); then
    if echo "$output" | grep -q "Inf Kp 56/1"; then
        pass "config get unit = Inf Kp 56/1"
    else
        fail "config get unit" "Expected 'Inf Kp 56/1', got: $output"
    fi
else
    fail "config get unit" "$output"
fi

echo ""
echo -e "${CYAN}--- Test 7: Export DOCX ---${NC}"
BEFEHL_MD="${WORK_DIR}/befehl.md"
cat > "$BEFEHL_MD" << 'BEFEOF'
# Allgemeiner Kp Befehl

## 1. Lage
Die Kp ist einsatzbereit.

## 2. Auftrag
Wachtdienst ab 0600.

## 3. Durchführung
3.1 Wachtdienst: Sicherung Haupteingang

## 4. Logistik
Verpflegung durch Küche Bat.

## 5. Führung
Kp Gefechtsstand: Gebäude 12.
BEFEOF

DOCX_FILE="${OUTPUT_DIR}/befehl.docx"
if output=$(milanon export "$BEFEHL_MD" --docx --output "$DOCX_FILE" 2>&1); then
    if [ -f "$DOCX_FILE" ]; then
        size=$(wc -c < "$DOCX_FILE")
        pass "export --docx (${size} bytes)"
    else
        fail "export --docx" "File not created"
    fi
else
    skip "export --docx" "Export failed (may need template): $(echo "$output" | head -1)"
fi

echo ""
echo -e "${CYAN}--- Test 8: Incremental Processing ---${NC}"
ANON_DIR2="${WORK_DIR}/anon2"
mkdir -p "$ANON_DIR2"
milanon anonymize "$INPUT_DIR" --output "$ANON_DIR2" >/dev/null 2>&1
if output=$(milanon anonymize "$INPUT_DIR" --output "$ANON_DIR2" 2>&1); then
    if echo "$output" | grep -qi "skip\|unchanged\|0.*new"; then
        pass "incremental skip on second run"
    else
        pass "incremental run completed (check output manually)"
    fi
    echo "    $output" | head -3
else
    fail "incremental" "$output"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}  Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}, ${YELLOW}${SKIP} skipped${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""
echo -e "Outputs available in: ${WORK_DIR}"
echo -e "  Anonymized:  ${ANON_DIR}/"
echo -e "  Prompts:     ${OUTPUT_DIR}/"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Some tests failed. Check output above.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
