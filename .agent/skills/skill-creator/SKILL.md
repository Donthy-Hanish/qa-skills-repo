---
name: skill-creator
description: "Creates new skills that ship at 100/A+ on the Agent Skills CLI rubric and conform to the agentskills.io specification. Produces six deliverables: SKILL.md, requirements.json, evals/trigger-eval.json, evals/test-prompts.json, scripts/ helpers, and references/ material. Tailored for teams using Antigravity as the IDE and Agent Skills CLI as the quality gate. Use this skill when someone says 'build a skill', 'create a skill', 'make a skill for', 'turn this into a skill', 'I keep repeating this prompt', 'can we automate this workflow', or wants to package a repeatable process into a reusable skill. Also use when someone asks to improve, edit, retrofit, or optimize an existing skill to reach 100/A+."
license: "Proprietary - CoStrategix internal"
compatibility: "Requires Node.js 18+, Agent Skills CLI installed, Antigravity IDE (optional but recommended for testing)."
metadata:
  version: "2.0.0"
  author: hanish-donthy
  category: knowledge-process
---

# Skill Creator for Antigravity + Agent Skills CLI

Build skills that ship at 100/A+ on the Agent Skills CLI quality rubric AND conform
to the agentskills.io specification. Every skill produces six deliverables:

```
skill-name/
├── SKILL.md              <- The skill itself (inline YAML description, anti-patterns, changelog)
├── requirements.json     <- Runtime dependencies for generated output
├── evals/
│   ├── trigger-eval.json <- 20 queries (10 should-trigger, 10 should-not-trigger)
│   └── test-prompts.json <- 3-5 realistic test prompts with evaluation criteria
├── scripts/              <- Automation hooks (at least 2-3 helpers)
│   └── *.{ps1,sh,py,js}
└── references/           <- On-demand reference material
    └── *.md, source files, project context
```

Optional but recommended:
```
└── assets/               <- Templates, sample data, schemas (per agentskills.io spec)
    └── *.json, *.csv, *.template
```

The distinction matters: `references/` = material the agent reads to understand the
domain. `assets/` = templates and data the agent uses as scaffolding. Don't mix them.

## The Process

Figure out where the user is and help them move forward:
- New skill → start at Step 1
- Existing skill to improve → jump to Step 4 (retrofit path)
- "Turn this conversation into a skill" → extract from chat history, start at Step 2

---

## Step 1: Capture Intent

Ask the user four questions. If the conversation already contains answers (they
described a workflow, showed examples, made corrections), extract those answers
first and confirm before asking for more.

1. **What should this skill do?**
   Get a concrete description, not a vague goal.
   Bad: "help with testing"
   Good: "generate structured test cases from user stories, covering positive,
   negative, boundary, and edge cases"

2. **When should it trigger?**
   What would someone actually type to need this skill? Collect 3-5 example phrases
   in the user's own words.

3. **What's the expected output?**
   A file? Structured text? A report? Get a concrete example if possible.

4. **What tools/frameworks does the team use?**
   Playwright? Robot Framework? YAML-driven suites? JUnit? This shapes the output
   AND the scripts/references bundle.

Do not proceed until you have clear answers to all four.

---

## Step 2: Research and Edge Cases

Before writing anything, dig deeper:

- What inputs will the skill receive? (files, text, URLs, screenshots?)
- What does "good" output look like? Ask for a real example.
- What are the edge cases? (empty inputs, malformed data, ambiguous requirements)
- Are there existing skills that overlap? If so, how is this one different?
- What domain knowledge does the skill need that Claude wouldn't know from training?
  (team conventions, framework specifics, project structure → these go in references/)
- What automation tasks recur in the workflow?
  (verify setup, switch config, open artifacts → these become scripts/)

Keep this conversation short — 2-3 questions max. The goal is to fill gaps, not
conduct an exhaustive interview.

---

## Step 3: Write the Six Deliverables

Create all six deliverables in one pass. Present them to the user together.

### Deliverable 1: SKILL.md

Follow the agentskills.io specification exactly AND meet the 100/A+ rubric.

#### Frontmatter rules

```yaml
---
name: skill-name
description: "Inline string starting with a verb in third person. Include both what the skill does AND when to use it. Be pushy with trigger phrases. Aim for 200-400 chars."
license: "Proprietary - CoStrategix internal"
compatibility: "Platform/runtime requirements if any. Skip if generic."
metadata:
  version: "1.0.0"
  author: hanish-donthy
  category: one-of-the-9-qa-categories
---
```

**Critical YAML rules** (learned the hard way):

- **NEVER use folded scalar (`>`) for the description.** Parsers collapse it to a
  single whitespace character and the description scores 0/20 on the Clarity check.
  Always use an inline quoted string.

  ```yaml
  # WRONG - scores 0/20
  description: >
    Long multi-line
    description here
  
  # RIGHT - scores 20/20
  description: "Long inline description here, all on one line, quoted."
  ```

- **Top-level custom fields are deprecated.** Put `version`, `author`, `category`
  inside `metadata:`. Spec parsers warn on unknown top-level keys.

- **`name` rules**: lowercase letters, numbers, hyphens only. Max 64 chars. No
  leading/trailing hyphens. No consecutive hyphens. Must match the parent directory.

- **`description` rules**: max 1024 chars. Third person ("Processes X" not "I can
  help with X" or "You can use this to..."). Be "pushy" — Anthropic has observed
  Claude under-triggers skills, so include many trigger phrases. Phrases like "Use
  this skill when..." or "Also trigger when..." help.

#### Body rules

- **Under 500 lines** total. If approaching this, split into references/ files.
- **Imperative form** ("Parse the input", "Generate the report").
- **Explain WHY, not just WHAT.** Models respond better to reasoning than rigid
  rules. If you find yourself writing ALWAYS or NEVER in caps, reframe as
  explanation. Example: instead of "NEVER edit generated files" write "Editing
  generated files is wiped on next recompile — modify the compiler source instead."

#### Required sections (for 100/A+ scoring)

The Agent Skills CLI rubric checks for specific sections. To hit 100/A+, include
ALL of these:

1. **Top-level heading** (`# Skill Name`)
2. **Purpose paragraph** explaining what + why
3. **"When to use" or "Usage" section** (15 points)
4. **Process / numbered steps** (20 points for ordered steps)
5. **Code blocks with examples** (25 points)
6. **References to specific tools, commands, file paths** (15 + 15 points)
7. **IF/THEN conditional logic** (10 points) — use explicit routing rules:
   ```markdown
   ## Routing - Where Is the User?
   - IF the user has not <X> yet → start at Phase 1
   - IF <Y> exists but no <Z> → start at Phase 3
   - IF <condition> → go to "Analyzing Results"
   ```
8. **Anti-patterns section** (20 points) — structured table, not just "Do NOT" rules:
   ```markdown
   ## Anti-Patterns and Common Mistakes
   | Anti-pattern | Why it's wrong | Do this instead |
   |--------------|----------------|-----------------|
   | Editing generated files | Wiped on next recompile | Modify the source generator |
   ```
9. **"Do NOT" constraints with reasoning** (15 points)
10. **Changelog at bottom** (15 points):
    ```markdown
    ## Changelog
    - **1.0.0** (YYYY-MM-DD) - Initial release.
    ```

#### Progressive disclosure

- Level 1: name + description (~100 tokens) — always loaded for all skills
- Level 2: SKILL.md body (<500 lines, <5000 tokens) — loaded when skill triggers
- Level 3: scripts/, references/, assets/ — loaded only when explicitly needed

Reference deeper material from the body with clear guidance on when to load it:
"IF the user asks how detection works internally → open
`references/<file>` and answer from source rather than guessing."

### Deliverable 2: requirements.json

Declare the runtime dependencies needed to execute the output this skill generates.

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "What these dependencies are for.",
  "runtime": {
    "node": ">=18.0.0",
    "powershell": ">=5.1"
  },
  "commands": [
    {
      "name": "k6",
      "version": ">=0.47.0",
      "install": "https://k6.io/docs/get-started/installation/",
      "check": "k6 version"
    }
  ],
  "node_packages": [
    {
      "name": "lighthouse",
      "version": "latest",
      "install": "npm install -g lighthouse",
      "purpose": "Performance auditing"
    }
  ],
  "python_packages": [
    {
      "name": "robotframework",
      "version": ">=7.0",
      "purpose": "Test execution"
    }
  ],
  "system": {
    "os": ["windows", "linux", "macos"],
    "notes": "Platform-specific gotchas."
  },
  "bundled_references": [
    "references/file1.md",
    "references/file2.js"
  ]
}
```

**Rules:**
- Only include dependencies needed to RUN the generated output, not to build/edit
  the skill itself.
- If the skill produces only markdown/text with no executable code, use empty
  arrays for commands/node_packages/python_packages.
- Match version against `metadata.version` in SKILL.md.

### Deliverable 3: evals/trigger-eval.json

20 evaluation queries for testing the skill's description accuracy.

```json
{
  "skill_name": "skill-name",
  "description": "Trigger evaluation: 10 queries that SHOULD activate the skill and 10 that should NOT.",
  "should_trigger": [
    {
      "id": "T01",
      "prompt": "realistic, messy user prompt with context",
      "reason": "Why this should activate the skill"
    }
  ],
  "should_not_trigger": [
    {
      "id": "N01",
      "prompt": "near-miss prompt that shares keywords but needs something different",
      "reason": "Why this should NOT activate the skill — what skill should handle it instead"
    }
  ]
}
```

**Rules for writing eval queries:**
- 10 should-trigger + 10 should-NOT-trigger
- Make them realistic — messy, casual, with typos, personal context, file paths,
  abbreviations. Not clean academic prompts.
- Should-trigger queries: vary the phrasing. Include cases where the user doesn't
  name the skill but clearly needs it.
- Should-NOT-trigger queries: these are the TRICKY near-misses. They share keywords
  with the skill but actually need a different skill. Always name the better-fit
  skill in the `reason` field.

### Deliverable 4: evals/test-prompts.json

3-5 realistic test prompts to validate the skill's actual output quality.

```json
{
  "skill_name": "skill-name",
  "description": "End-to-end test prompts. Each includes explicit evaluation criteria.",
  "test_prompts": [
    {
      "id": 1,
      "prompt": "Realistic prompt a user would type",
      "expected_output": "What good output looks like — format, key sections, quality markers",
      "evaluation_criteria": [
        "Output includes <specific element>",
        "Output uses <specific format>",
        "Output does NOT <specific anti-pattern>"
      ]
    }
  ]
}
```

**Rules:**
- Cover simple, complex, and edge cases.
- Evaluation criteria must be objectively checkable.
- If the skill produces files, describe what each file should contain.

### Deliverable 5: scripts/ directory

At least 2-3 helper scripts that automate manual steps in the workflow. Scripts
should be self-contained and document their parameters.

Common script patterns:

- **preflight check** — verifies tools, paths, dependencies are in place before
  running the workflow
- **setup helper** — bootstraps a working directory, copies templates, generates
  config files
- **runner / orchestrator** — runs the main workflow with sensible defaults
- **artifact helper** — opens the latest output, switches active configs, packages
  results

Languages: PowerShell (`.ps1`) for Windows-heavy workflows, Bash (`.sh`) for cross-
platform, Python (`.py`) for logic-heavy helpers, Node (`.js`) for npm-ecosystem
work.

Skills WITHOUT a scripts/ directory cap at 75/100 on the rubric (loses 25 points).

### Deliverable 6: references/ directory

On-demand documentation and source material. Loaded only when the SKILL.md body
explicitly directs the agent to read a file.

Common reference patterns:

- **methodology.md** — how to reason about the domain, decision trees, frameworks
- **project-context.md** — architecture, file map, conventions of a target project
- **api-reference.md** — domain-specific API or framework details
- **source files** — actual code the skill operates on (compilers, configs, parsers)
- **templates** — file templates the skill uses as starting points

For agentskills.io spec compliance, prefer naming files by content rather than
generic names. `playbook.md` is fine. `REFERENCE.md` and `FORMS.md` are spec-
suggested patterns but lowercase descriptive names work equally well.

Files in references/ are read on demand. Keep each one focused — smaller files
mean less wasted context when the agent only needs one section.

---

## Step 4: Review with the User

Present all six deliverables and ask:

> Here's what I've created:
> 1. **SKILL.md** — [brief summary]
> 2. **requirements.json** — runtime dependencies
> 3. **trigger-eval.json** — 20 queries for triggering accuracy
> 4. **test-prompts.json** — [N] end-to-end test prompts
> 5. **scripts/** — [N] helper scripts ([list names])
> 6. **references/** — [N] reference files ([list names])
>
> Want to review each one, or should we go straight to validation?

Give the user a chance to adjust before proceeding. Common feedback:
- "The description is missing [trigger phrase]" → update description
- "Add a test case for [scenario]" → add to test-prompts.json
- "This near-miss should actually trigger" → flip it in trigger-eval.json
- "We don't need [script]" → remove it, but consider adding a different helper

---

## Step 5: Validate with Agent Skills CLI

Guide the user to run the quality gate:

```bash
# Validate structure against agentskills.io spec
skills validate ./skill-name

# Score quality (TARGET: 100/A+, minimum acceptable: 85)
skills score ./skill-name --verbose

# Check for conflicts with existing skills
skills sandbox ./skill-name
```

If the score is below 100, the verbose output will list exactly what's missing.
Most common gaps:

| Gap | Fix |
|-----|-----|
| Description 0/20 (says "1 char") | Switched to inline string — folded `>` collapses to whitespace |
| No conditional logic 0/10 | Add IF/THEN routing rules in the body |
| No scripts/ directory 0/25 | Add 2-3 helper scripts |
| No anti-patterns 0/20 | Add the structured anti-patterns table |
| No changelog 0/15 | Add Changelog section at bottom |

Re-validate after every fix.

---

## Step 6: Test in Antigravity

Sync the skill to Antigravity:

```bash
skills install ./skill-name -a antigravity
```

Test each prompt from test-prompts.json:
1. Type the prompt in Antigravity
2. Did the skill trigger? (check against trigger-eval expectations)
3. Review the output against evaluation_criteria
4. Note what worked and what didn't

Track results in a simple table:

```
| Prompt | Triggered? | Output Quality | Notes |
|--------|-----------|---------------|-------|
| #1     | Yes       | Good          |       |
| #2     | Yes       | Missing X     | Fix Y |
```

---

## Step 7: Iterate

Based on test results:

1. **Triggering issues** → update the description. Add missing trigger phrases.
   Remove overly broad phrases causing false positives.
2. **Output quality issues** → update body instructions. Add examples. Explain WHY.
3. **Missing edge cases** → add to process steps, examples, and test-prompts.json.
4. **Repeated agent work** → bundle as a script in scripts/ and reference from body.
5. **Missing domain knowledge** → add to references/ with a clear "when to load" cue
   in the body.

Re-validate and re-score after each change. Repeat until 100/A+.

---

## Step 8: Ship

```bash
# Final validation pass
skills validate ./skill-name
skills score ./skill-name --verbose

# Commit to the project repo
cp -r ./skill-name .agent/skills/
git add .agent/skills/skill-name/
git commit -m "feat: add skill-name skill (100/A+)"
git push
```

The team gets the skill on their next git pull. Antigravity picks it up
automatically from `.agent/skills/`.

---

## Retrofitting an Existing Skill to 100/A+

If a skill exists but scores below 100:

1. Run `skills score ./skill-name --verbose` to identify gaps.
2. Apply fixes in order of point value (highest first):
   - **25 points**: scripts/ directory
   - **20 points**: anti-patterns section
   - **20 points**: description ≥50 chars and parseable
   - **15 points**: changelog
   - **10 points**: IF/THEN conditional logic
3. Preserve the original skill name. Never rename during retrofit — it breaks
   references and team habits.
4. Bump the version in metadata (1.0.0 → 1.1.0 for content additions, 2.0.0 for
   structural changes).
5. Add a changelog entry describing what changed.

---

## Anti-Patterns and Common Mistakes (in skill authoring itself)

Do NOT do any of the following:

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|-----------------|
| Using folded YAML scalar (`>`) for description | Parsers collapse it to whitespace; description scores 0/20 | Use inline quoted string `description: "..."` |
| Putting `version` at top level of frontmatter | Spec-noncompliant; strict parsers warn | Move under `metadata:` |
| Writing description in first/second person ("I help with..." or "You can use this to...") | Causes discovery problems per Anthropic guidance | Third person: "Processes X" |
| Using ALL-CAPS imperatives (ALWAYS, NEVER, MUST) without reasoning | Agent follows letter but misses edge cases | State the rule, then explain WHY |
| Skipping scripts/ because "the skill is just docs" | Caps the score at 75/100 | Add 2-3 helpers — even simple preflight checks count |
| Writing eval queries that are clean and academic | Doesn't reflect real user prompts; triggering breaks in production | Write messy, casual, typo-laden prompts |
| Should-not-trigger queries that share NO keywords with the skill | Trivial negatives don't stress-test triggering | Use near-misses that share keywords but need a different skill |
| Treating "score 70+" as the bar | Leaves 30 points on the table; the skill is mediocre | Target 100/A+ — every check has a clear fix |
| Mixing references/ and assets/ contents | Tooling treats them differently (loading, indexing) | Documentation in references/, templates+data in assets/ |
| Renaming a skill during retrofit | Breaks all existing trigger evals, project references, team habits | Keep the name; bump the version |
| Description that's too narrow ("triggers only on exact phrase X") | Skill never triggers in production because real prompts vary | Be "pushy" — list many trigger phrases including casual variants |
| Description that's too broad ("helps with anything related to X") | Skill triggers on everything; user gets the wrong skill | Include explicit "Use when..." AND "Do not trigger when..." cues |
| Writing the body to be exhaustive (1000+ lines) | Token-heavy on every invocation; agent skims past key sections | Stay under 500 lines; push detail to references/ |

---

## Quick Reference: Deliverable Checklist

Before presenting to the user, verify:

**SKILL.md frontmatter:**
- [ ] `name`: lowercase, hyphens, ≤64 chars, matches directory name
- [ ] `description`: inline string (NOT folded `>`), 50-1024 chars, third person,
      includes "Use this skill when..." trigger phrases
- [ ] `license`: declared (even if internal/proprietary)
- [ ] `compatibility`: declared IF platform-specific
- [ ] `metadata`: version, author, category

**SKILL.md body:**
- [ ] ≤500 lines
- [ ] Top-level heading + Purpose paragraph
- [ ] "When to use" or "Usage" section
- [ ] Numbered process steps
- [ ] Code blocks with examples
- [ ] References to specific tools/commands/paths
- [ ] IF/THEN conditional logic (routing rules)
- [ ] Anti-patterns table (mistake / why wrong / do instead)
- [ ] "Do NOT" constraints WITH reasoning
- [ ] Changelog section at bottom

**evals/trigger-eval.json:**
- [ ] 20 queries total (10 should-trigger, 10 should-not-trigger)
- [ ] Queries are realistic, messy, varied in length and formality
- [ ] Should-not-trigger queries are genuine near-misses
- [ ] Each negative names the better-fit skill in the reason field

**evals/test-prompts.json:**
- [ ] 3-5 prompts covering simple, complex, and edge cases
- [ ] Each has objectively checkable evaluation_criteria

**requirements.json:**
- [ ] Lists only runtime dependencies (not build-time)
- [ ] Matches `metadata.version` in SKILL.md
- [ ] Empty arrays where no deps (not omitted)

**scripts/:**
- [ ] At least 2-3 helper scripts
- [ ] Each documents its parameters
- [ ] Each handles edge cases (missing files, wrong env)

**references/:**
- [ ] Material the skill body explicitly directs the agent to load
- [ ] Each file focused on a single topic
- [ ] No dump of generic Claude knowledge — only domain-specific or project-
      specific content

**Final score check:**
- [ ] `skills score ./skill-name --verbose` shows 100/A+
- [ ] `skills validate ./skill-name` passes spec compliance
- [ ] `skills sandbox ./skill-name` shows no conflicts

---

## Changelog

- **2.0.0** (2026-06-03) — Major update. Added 100/A+ rubric requirements as
  explicit deliverables. Added scripts/ and references/ as required deliverables
  (now 6 total, up from 4). Added agentskills.io spec compliance (metadata block,
  license field, compatibility field, assets/ distinction). Added Anthropic
  official guidance (third-person, pushy descriptions, why-not-rules). Added
  YAML folded-scalar warning. Added anti-patterns table for skill authoring.
  Bumped target score from 70 → 100. Added retrofit path for upgrading existing
  skills.
- **1.0.0** (2026-04-XX) — Initial release. Four deliverables: SKILL.md,
  requirements.json, evals/trigger-eval.json, evals/test-prompts.json. Eight-step
  process. Quick reference checklist.
