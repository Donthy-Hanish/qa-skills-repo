# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of reusable AI skills for QA workflows, consumed by the Antigravity IDE. Skills live in `.agent/skills/` and are validated by the Agent Skills CLI (`agent-skills-cli`).

## Commands

### Agent Skills CLI (requires `npm install -g agent-skills-cli`)

```powershell
# Run from inside .agent/skills/<skill-name>/ or pass the path
skills validate .\skill-name              # Check structure against agentskills.io spec
skills score .\skill-name --verbose       # Score quality — target 100/A+ (CI minimum: 70)
skills test .\skill-name                  # Run trigger-eval.json test suite
skills sandbox .\skill-name              # Check for conflicts with other skills
skills install .\skill-name -a antigravity  # Deploy to Antigravity for manual testing
```

### Eval Tools (PowerShell, from repo root)

```powershell
# Anthropic-based eval runner (compares with_skill vs without_skill)
$env:ANTHROPIC_API_KEY = "sk-ant-..."
cd .agent/skills
..\..\tools\run-skill-eval.ps1 -SkillName appium-mobile-tester
..\..\tools\run-skill-eval.ps1 -SkillName appium-mobile-tester -Model claude-haiku-4-5-20251001 -OutputReport ..\..\eval-reports

# Reference integrity check (finds missing/orphaned files)
cd .agent/skills
..\..\tools\validate-skill-references.ps1
..\..\tools\validate-skill-references.ps1 -SkillName appium-mobile-tester

# Batch evals via agent-skills-eval.yaml (uses Groq by default — set GROQ_API_KEY)
npx agent-skills-eval --config agent-skills-eval.yaml
```

### Skill Lifecycle

```powershell
# 1. Build skill (in Antigravity or with skill-creator)
# 2. Validate all four gates
skills validate .\skill-name
skills score .\skill-name --verbose   # Must be 100/A+
skills test .\skill-name
skills sandbox .\skill-name

# 3. Check reference integrity
cd .agent/skills && ..\..\tools\validate-skill-references.ps1 -SkillName <skill-name>

# 4. Commit
git add .agent/skills/<skill-name>/
git commit -m "feat(skills): add <skill-name>"
```

## Skill Architecture

Every skill under `.agent/skills/<skill-name>/` follows this structure:

```
skill-name/
├── SKILL.md              # The skill: frontmatter + instructions
├── requirements.json     # Runtime dependencies for generated output
├── evals/
│   ├── trigger-eval.json # 20 queries testing when skill should/should not fire
│   └── test-prompts.json # 3-5 prompts with verifiable evaluation_criteria
├── scripts/              # Helper automation (≥2 required — absence costs 25 pts)
│   └── *.{ps1,sh,py,js}
└── references/           # On-demand domain docs loaded when SKILL.md directs it
    └── *.md
```

`references/` = material the agent reads to understand the domain. `scripts/` = automation the user runs. Do not mix them. An `assets/` directory (templates/data) is optional per spec.

## SKILL.md Rules (Critical — violations drop score to 0 on specific checks)

**Frontmatter:**
- `description:` must be an **inline quoted string** — never folded scalar (`>`). Folded collapses to whitespace and scores 0/20 on Clarity.
- `description:` must be under 200 chars and start with an action verb (Generate, Run, Analyze...).
- No `version:` key at the top level — move it under `metadata:`.
- No unknown/extra keys.

```yaml
# Correct
---
name: appium-mobile-tester
description: "Generate Python + pytest + Appium test suites for mobile apps..."
---

# Wrong — collapses to whitespace, scores 0
---
name: appium-mobile-tester
description: >
  Generate Python + pytest...
---
```

**Body (required sections for 100/A+):**
1. Top-level heading + intro paragraph
2. When to Use (bullet list of trigger phrases)
3. Do NOT Use (explicit exclusions)
4. Prerequisites
5. Routing / Decision Rules (IF/THEN conditional logic)
6. Core Workflow (numbered steps)
7. Reference Files table — three columns: File | What it is | When to load
8. Scripts table — three columns: Script | Purpose | When to run
9. Examples (≥2 with input and expected output)
10. Anti-Patterns table (≥5 entries: pattern | why wrong | fix)
11. Troubleshooting table (≥4 entries: symptom | fix)
12. Changelog at bottom

Body must stay under 500 lines. Push heavy content to `references/`.

## Eval File Formats

**trigger-eval.json** — each entry needs `id`, `prompt`, `should_trigger` (boolean), `rationale`. Minimum 10 entries, ≥60% should-trigger, ≥3 should-NOT-trigger. Write messy realistic prompts, not clean academic ones. Negative cases must be genuine near-misses (same keywords, different need).

**test-prompts.json** — each entry needs `id`, `prompt`, `expected_output`, `expectations` (array of specific, verifiable strings). Minimum 3 prompts covering happy path + at least one edge case.

## CI

GitHub Actions (`.github/workflows/skill-quality.yml`) runs on PRs touching `.agent/skills/**`. It runs `skills validate` and `skills score` (minimum 70). PRs fail if any skill scores below 70 or fails validation.

Internal target is 100/A+ (not 70). The CI threshold is a floor, not the goal.

## Reference Integrity

`tools/validate-skill-references.ps1` checks that every file cited in SKILL.md exists on disk AND that no files on disk are orphaned (exist but not mentioned). Run it before every commit. CI does not run it — it's a local gate.

## Key Files

- `docs/skill-standardization-checklist.md` — exhaustive checklist for standardizing or reviewing a skill
- `agent-skills-eval.yaml` — batch eval config (Groq by default; swap `target`/`judge`/`baseUrl`/`apiKeyEnv` for Anthropic or OpenAI)
- `.agent/skills/skill-creator/SKILL.md` — meta-skill that guides building new skills; read it before authoring a skill from scratch
- `tools/run-skill-eval.ps1` — Anthropic-native eval runner that does with/without skill comparison and writes HTML reports to `eval-reports/`
