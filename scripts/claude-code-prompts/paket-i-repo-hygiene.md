# MEGA-PROMPT: Paket I — Repo-Hygiene & Frühlingsputz
# MODEL: Sonnet

## Context
Read CLAUDE.md. This is a housekeeping task — clean up the repo, remove stale files, update .gitignore.

## Branch
```bash
git checkout -b chore/repo-hygiene
```

## Task 1: .gitignore Update

Read the current `.gitignore`. Add these entries if missing:

```
# macOS
.DS_Store
**/.DS_Store

# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/

# Virtual environment
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Test output (generated at runtime, not committed)
test_output/

# Source documents (too large for git, contain PII)
ZZ_Unterlagen Review Product Design/

# MilAnon runtime
.milanon/
*.db

# Streamlit
.streamlit/
```

## Task 2: Remove files that should be gitignored

Check if any of these are tracked by git and remove them:
```bash
git rm -r --cached .DS_Store 2>/dev/null
git rm -r --cached '**/.DS_Store' 2>/dev/null
git rm -r --cached __pycache__/ 2>/dev/null
git rm -r --cached test_output/ 2>/dev/null
git rm -r --cached .pytest_cache/ 2>/dev/null
# Check if ZZ_Unterlagen is tracked
git ls-files 'ZZ_Unterlagen Review Product Design/' | head -5
# If tracked, remove from git (keep local):
# git rm -r --cached 'ZZ_Unterlagen Review Product Design/'
```

## Task 3: Delete stale branches

List and delete merged feature branches:
```bash
git branch | grep -v main
# Delete each merged branch:
git branch -d feat/e14-doctrine-extraction 2>/dev/null
git branch -d feat/e15-workflow-infrastructure 2>/dev/null
git branch -d feat/e15-workflow-templates 2>/dev/null
git branch -d feat/e15-layer-templates 2>/dev/null
git branch -d feat/e17-docx-export 2>/dev/null
git branch -d feat/e15-cli-integration 2>/dev/null
```

## Task 4: Archive or delete outdated docs

These docs are superseded by newer versions. Move them to `docs/archive/`:

```bash
mkdir -p docs/archive
```

| File | Superseded by | Action |
|---|---|---|
| `docs/BACKLOG.md` | `docs/ROADMAP.md` (v2, has all stories) | Move to archive |
| `docs/PRD.md` | `docs/PRODUCT_DESIGN_COMMAND_ASSISTANT.md` | Move to archive |
| `docs/IMPLEMENTATION_PLAN.md` | `docs/ROADMAP.md` + `docs/SPRINT_PLAN.md` | Move to archive |
| `docs/PROJECT_SUMMARY.md` | `docs/SESSION_HANDOVER.md` | Move to archive |
| `docs/PRODUCT_VISION_V2.md` | `docs/PRODUCT_DESIGN_COMMAND_ASSISTANT.md` | Move to archive |

Add a note in `docs/archive/README.md`:
```markdown
# Archived Documents

These documents are from earlier project phases and have been superseded.
Kept for historical reference only.

| Document | Superseded by | Date archived |
|---|---|---|
| BACKLOG.md | ROADMAP.md | 2026-03-25 |
| PRD.md | PRODUCT_DESIGN_COMMAND_ASSISTANT.md | 2026-03-25 |
| IMPLEMENTATION_PLAN.md | ROADMAP.md + SPRINT_PLAN.md | 2026-03-25 |
| PROJECT_SUMMARY.md | SESSION_HANDOVER.md | 2026-03-25 |
| PRODUCT_VISION_V2.md | PRODUCT_DESIGN_COMMAND_ASSISTANT.md | 2026-03-25 |
```

## Task 5: Verify directory structure is clean

Print the top-level tree and verify it matches the expected structure:
```
Anonymizer_Tool_Army/
├── .claude/
├── .git/
├── .gitignore
├── .venv/                          (gitignored)
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE                         (create if missing — MIT)
├── README.md
├── data/
│   ├── doctrine/                   (11 reglemente + INDEX + extracts + skeletons)
│   ├── military_units.csv
│   ├── swiss_municipalities.csv
│   └── templates/                  (role.md, rules.md, workflows/, docx/)
├── docs/
│   ├── architecture/               (ADR-001 through ADR-013)
│   ├── archive/                    (old docs)
│   ├── OPEN_DECISIONS.md
│   ├── PRODUCT_DESIGN_COMMAND_ASSISTANT.md
│   ├── PRODUCT_DESIGN_TF17_APPENDIX.md
│   ├── ROADMAP.md
│   ├── SESSION_HANDOVER.md
│   ├── SPRINT_PLAN.md
│   ├── STRATEGIC_ANALYSIS.md
│   └── USER_JOURNEY_WK2026.md
├── pyproject.toml
├── scripts/
│   └── claude-code-prompts/        (mega-prompts for dev sessions)
├── src/milanon/
├── tests/
└── (NO test_input/ or test_output/ committed)
```

## Task 6: Create LICENSE file (if missing)

```
MIT License

Copyright (c) 2026 MilAnon Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Files NOT to touch:
- `src/` (any Python source code)
- `tests/` (any test file)
- `data/doctrine/` (any doctrine file)
- `data/templates/` (any template)

## Run and verify:
```bash
python -m pytest tests/ -x --tb=short  # all tests must still pass
git status  # check what changed
```

## Commit
```bash
git add -A
git commit -m "chore: repo hygiene — gitignore, archive stale docs, LICENSE, branch cleanup

- .gitignore: comprehensive exclusion list (DS_Store, pycache, test_output, ZZ_Unterlagen)
- docs/archive/: moved 5 superseded documents with README
- LICENSE: MIT license added
- Stale branches deleted
- Tracked .DS_Store and __pycache__ removed from git"
```
