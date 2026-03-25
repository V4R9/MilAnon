# FR-017: Sprint Plan — Two-Tier Anonymization

> Sprint Duration: 1 session (~4-6h with 6 parallel Claude Code instances)
> Model: Sonnet for all pakets (domain logic, no complex creative decisions)
> Branch: `feat/two-tier-anonymization`
> Prerequisite: CR-001/002/003 merged (Paket N)

---

## Sprint Architecture

```
Round 1 (4 parallel — zero file conflicts):
  Claude 1: Paket O — Domain Layer (entities.py + anonymization_level.py + tests)
  Claude 2: Paket P — UseCase + CLI (anonymize.py + main.py + tests)
  Claude 3: Paket Q — Context & Templates (generate_context.py + role.md + rules.md)
  Claude 4: Paket R — Repository + Config (sqlite_repository.py + config + tests)

Round 2 (2 parallel — depends on Round 1):
  Claude 5: Paket S — GUI + Project Generator (app.py + generate_project.py)
  Claude 6: Paket T — Documentation + E2E Test (CLAUDE.md + BACKLOG.md + E2E test)
```

## Conflict Matrix (Round 1 = zero conflicts)

| File | O | P | Q | R |
|---|---|---|---|---|
| domain/entities.py | WRITE | read | — | — |
| domain/anonymization_level.py | CREATE | read | — | — |
| usecases/anonymize.py | — | WRITE | — | — |
| cli/main.py | — | WRITE | — | — |
| usecases/generate_context.py | — | — | WRITE | — |
| data/templates/*.md | — | — | WRITE | — |
| adapters/repositories/sqlite_repository.py | — | — | — | WRITE |

## Mega-Prompts

Each mega-prompt is in a separate file:
- `scripts/claude-code-prompts/paket-o-domain-level.md`
- `scripts/claude-code-prompts/paket-p-usecase-cli.md`
- `scripts/claude-code-prompts/paket-q-templates.md`
- `scripts/claude-code-prompts/paket-r-repository.md`
- `scripts/claude-code-prompts/paket-s-gui-project.md`
- `scripts/claude-code-prompts/paket-t-docs-e2e.md`

## Execution

### Pre-Sprint
- [ ] CR-001/002/003 merged (Paket N)
- [ ] CR-006/009 manually fixed
- [ ] All tests green on main

### Round 1 (Parallel)
```bash
# Terminal 1
/model sonnet
Read scripts/claude-code-prompts/paket-o-domain-level.md and execute all instructions.

# Terminal 2
/model sonnet
Read scripts/claude-code-prompts/paket-p-usecase-cli.md and execute all instructions.

# Terminal 3
/model sonnet
Read scripts/claude-code-prompts/paket-q-templates.md and execute all instructions.

# Terminal 4
/model sonnet
Read scripts/claude-code-prompts/paket-r-repository.md and execute all instructions.
```

### Integration Check
- [ ] Merge all Round 1 into branch, resolve minor conflicts
- [ ] `python -m pytest tests/ -x --tb=short`

### Round 2 (Parallel)
```bash
# Terminal 5
/model sonnet
Read scripts/claude-code-prompts/paket-s-gui-project.md and execute all instructions.

# Terminal 6
/model sonnet
Read scripts/claude-code-prompts/paket-t-docs-e2e.md and execute all instructions.
```

### Post-Sprint
- [ ] Full test suite green
- [ ] Smoke test: `milanon anonymize --level dsg` vs `--level full`
- [ ] Merge to main, tag v0.6.0
