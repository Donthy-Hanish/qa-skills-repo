# Skill Standardization Checklist

Apply this checklist to every skill in the qa-skills-repo to ensure uniform structure,
quality, and scoring. Target: 100/A+ on all four CLI checks.

## How to Use

Run through each section for every skill. Mark items as PASS, FAIL, or N/A.
Fix all FAILs before committing.

---

## 1. FRONTMATTER (SKILL.md lines 1-4)

- [ ] Uses `---` delimiters (not `***` or other)
- [ ] `name:` field matches folder name exactly
- [ ] `description:` is an inline quoted string (wrapped in `"..."`)
- [ ] `description:` is under 200 characters
- [ ] `description:` starts with an action verb (Generate, Run, Analyze, Build, etc.)
- [ ] No `version:` in frontmatter (not allowed by packager)
- [ ] No extra/unknown keys in frontmatter

**Example of correct frontmatter:**
```yaml
---
name: appium-mobile-tester
description: "Generate Python + pytest + Appium test suites for mobile apps - native Android, iOS, React Native, Flutter, or hybrid. Covers POM, locator chains, gestures, and cross-platform configs."
---
```

---

## 2. REQUIRED FILES

- [ ] `SKILL.md` exists at skill root
- [ ] `requirements.json` exists at skill root
- [ ] `evals/trigger-eval.json` exists
- [ ] `evals/test-prompts.json` exists

---

## 3. REQUIRED SECTIONS IN SKILL.md (in this order)

- [ ] **Title heading** (`# Skill Name`) - first line after frontmatter
- [ ] **Intro paragraph** - 1-2 sentences explaining what the skill does
- [ ] **When to Use** - bullet list of activation triggers
- [ ] **Do NOT Use** - bullet list of exclusions (what this skill is NOT for)
- [ ] **Prerequisites** - tools, packages, environment needed
- [ ] **Routing / Decision Rules** - IF/THEN conditional logic for request classification
- [ ] **Core Workflow** - numbered steps or flow sections
- [ ] **Reference Files table** - three-column table (see Section 6 below)
- [ ] **Scripts table** - three-column table (see Section 6 below)
- [ ] **Examples** - at least 2 worked examples showing input and expected output
- [ ] **Anti-Patterns and Pitfalls** - table of common mistakes with fixes
- [ ] **Troubleshooting** - table of symptoms and fixes
- [ ] **Changelog** - version history with dates

---

## 4. FORMATTING RULES

- [ ] No consecutive blank lines anywhere in SKILL.md
- [ ] No TODO, FIXME, placeholder, TBD, HACK, or XXX text anywhere
- [ ] No em dashes - use hyphens, commas, or restructured sentences
- [ ] Code blocks use correct language identifiers (python, bash, powershell, json, etc.)
- [ ] Tables use `|---|---|---|` separator format
- [ ] Section headings use `##` (not `###` for top-level sections)
- [ ] File is under 500 lines (move heavy content to references/)

---

## 5. CONTENT QUALITY

- [ ] Test data uses meaningful domain-appropriate names (not "test123", "user1", "foo")
- [ ] Action verbs in method/function names (enter_username, tap_login, not handle_field)
- [ ] Assertions have descriptive failure messages
- [ ] Environment-specific values come from env vars with sensible defaults, never hardcoded
- [ ] All code examples are complete and runnable (no "..." or incomplete snippets)
- [ ] Anti-patterns table has at least 5 entries with three columns: pattern, why it breaks, fix
- [ ] Troubleshooting table has at least 4 entries with two columns: symptom, fix

---

## 6. REFERENCE AND SCRIPT TABLES (THE UNIFORM PATTERN)

Every skill that has references/ or scripts/ directories MUST include these tables.
Both tables use the three-column format.

### Reference Files Table

```markdown
## Reference Files

| File | What it is | When to load |
|---|---|---|
| `references/filename.md` | One-line description | Trigger condition for loading |
```

**Rules:**
- [ ] Table exists if references/ directory exists
- [ ] Every file in references/ has a row in the table
- [ ] Every row in the table maps to a real file on disk
- [ ] "When to load" column gives a specific trigger (not vague "when needed")
- [ ] Reference files use progressive disclosure (loaded on demand, not upfront)

### Scripts Table

```markdown
## Scripts

| Script | Purpose | When to run |
|---|---|---|
| `scripts/filename.sh` | One-line description | Trigger condition for running |
```

**Rules:**
- [ ] Table exists if scripts/ directory exists
- [ ] Every file in scripts/ has a row in the table
- [ ] Every row in the table maps to a real file on disk
- [ ] "When to run" column ties to a specific workflow step or error condition

**Bad examples (do NOT do this):**
```
| Script | Purpose |                    <-- Missing "When to run" column
| `scripts/setup.sh` | Sets up stuff |  <-- Vague purpose, no trigger
```

**Good examples:**
```
| Script | Purpose | When to run |
|---|---|---|
| `scripts/verify-setup.sh` | Check Appium, ADB, Node.js, Python, and connected devices | Before first test run, or when "Could not start session" errors appear |
| `scripts/preflight.ps1` | Verify k6, node, and the project directory exist | Before first test run, or when setup errors appear |
```

---

## 7. EVALS QUALITY

### trigger-eval.json
- [ ] At least 10 test cases total
- [ ] At least 60% should-trigger cases
- [ ] At least 3 should-NOT-trigger cases
- [ ] Each case has: id, prompt, should_trigger (boolean), rationale
- [ ] Negative cases cover adjacent/similar skills that should NOT trigger
- [ ] Prompts are realistic (what a real user would type, not synthetic)

### test-prompts.json
- [ ] At least 3 test prompts
- [ ] Each prompt has: id, prompt, expected_output, expectations (array)
- [ ] Expectations are specific and verifiable (not vague "output should be good")
- [ ] At least one prompt tests the primary/happy path
- [ ] At least one prompt tests an edge case or secondary flow

---

## 8. REQUIREMENTS.JSON

- [ ] `skill_name` matches folder name and SKILL.md frontmatter name
- [ ] `runtime.language` specified (python, node, etc.)
- [ ] `runtime.min_version` specified
- [ ] Every dependency has: name, version (or constraint), purpose
- [ ] Purpose is a human-readable sentence (not just the package name restated)
- [ ] Optional dependencies are in a separate `optional` array
- [ ] No credentials, tokens, or secrets anywhere in the file

---

## 9. CLI SCORING GATES (must pass all four)

Run these in order. All must pass before committing.

```powershell
skills validate .\skill-name              # Must show: Skill is valid
skills score .\skill-name --verbose       # Must show: 100/100 A+
skills test .\skill-name                  # Must show: 100% (0 failed)
skills sandbox .\skill-name               # Must show: Grade A (100%)
```

- [ ] `skills validate` - VALID
- [ ] `skills score --verbose` - 100/100 A+, all 20 checks green
- [ ] `skills test` - 100%, 0 failed
- [ ] `skills sandbox` - Grade A (100%), no conflicts

---

## 10. REFERENCE INTEGRITY

Run the validator script:

```powershell
..\..\tools\validate-skill-references.ps1 -SkillName <skill-name>
```

- [ ] All referenced files exist on disk
- [ ] No orphaned files (on disk but not in SKILL.md)
- [ ] Required files all present (SKILL.md, requirements.json, evals/)

---

## QUICK FIX REFERENCE

| Common issue | Fix |
|---|---|
| Description over 200 chars | Trim to summary, move detail to body "When to Use" section |
| Placeholder text (TODO/FIXME) | Replace with actual content or remove |
| Consecutive blank lines | Collapse double blanks to single |
| Missing "When to Use" section | Add after intro paragraph with bullet list |
| Scripts table missing third column | Add "When to run" column with specific triggers |
| References table missing third column | Add "When to load" column with specific triggers |
| `version:` in frontmatter | Remove the line (not allowed by packager) |
| YAML folded scalar description | Change `>` to inline `"..."` quoted string |
| Score 85 on Clarity | Usually the blank lines or missing "When to Use" |
| Sandbox shows B (80%) | Usually description length + placeholder text |

---

## APPLYING TO EXISTING SKILLS

Priority order for fixing existing skills:

1. Frontmatter description (under 200 chars, inline quoted)
2. Remove TODO/FIXME/placeholder text
3. Remove consecutive blank lines
4. Add/fix Reference Files and Scripts tables to three-column format
5. Add missing sections (When to Use, Anti-Patterns, Changelog)
6. Run all four CLI checks
7. Run reference integrity validator

For new skills contributed via PR, all items must pass before merge.
