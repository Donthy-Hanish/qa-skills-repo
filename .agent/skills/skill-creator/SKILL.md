---
name: skill-creator
description: >
  Create new skills that output four deliverables: a SKILL.md file, an eval
  set (trigger-eval.json), test prompts (test-prompts.json), and a
  requirements.json declaring runtime dependencies. Tailored for
  teams using Antigravity as their IDE and Agent Skills CLI as the quality gate.
  Use this skill when someone says "build a skill", "create a skill", "make a
  skill for", "turn this into a skill", "I keep repeating this prompt", "can we
  automate this workflow", or wants to package a repeatable process into a
  reusable skill. Also trigger when someone asks to improve, edit, or optimize
  an existing skill.
---

# Skill Creator for Antigravity + Agent Skills CLI

Build skills that ship with everything needed to validate, test, and install them.
Every skill you create produces four files:

```
skill-name/
├── SKILL.md              <- The skill itself
├── requirements.json     <- Runtime dependencies for generated output
├── evals/
│   ├── trigger-eval.json <- 20 queries for description optimization
│   └── test-prompts.json <- 3-5 realistic test prompts with expected outputs
```

## The Process

Figure out where the user is and help them move forward:
- New skill → start at Step 1
- Existing skill to improve → jump to Step 4
- "Turn this conversation into a skill" → extract from chat history, start at Step 2

---

## Step 1: Capture Intent

Ask the user four questions. If the conversation already contains answers
(they described a workflow, showed examples, made corrections), extract
those answers first and confirm before asking for more.

1. **What should this skill do?**
   Get a concrete description, not a vague goal.
   Bad: "help with testing"
   Good: "generate structured test cases from user stories, covering
   positive, negative, boundary, and edge cases"

2. **When should it trigger?**
   What would someone actually type to need this skill?
   Collect 3-5 example phrases in the user's own words.

3. **What's the expected output?**
   A file? Structured text? A report? Get a concrete example if possible.

4. **What tools/frameworks does the team use?**
   Playwright? Jest? YAML-driven suites? JUnit? This shapes the output.

Do not proceed until you have clear answers to all four.

---

## Step 2: Research and Edge Cases

Before writing anything, dig deeper:

- What inputs will the skill receive? (files, text, URLs, screenshots?)
- What does "good" output look like? Ask for a real example.
- What are the edge cases? (empty inputs, malformed data, ambiguous requirements)
- Are there existing skills that overlap? If so, how is this one different?

Keep this conversation short — 2-3 questions max. The goal is to fill gaps,
not conduct an exhaustive interview.

---

## Step 3: Write the Four Deliverables

Create all four files in one pass. Present them to the user together.

### Deliverable 1: SKILL.md

Follow the agentskills.io specification exactly:

**Frontmatter rules:**
- `name`: lowercase, numbers, hyphens only. Max 64 chars. Must not start/end
  with hyphen. No consecutive hyphens. Must match the parent directory name.
- `description`: max 1024 chars. Must describe BOTH what the skill does AND
  when to use it. Be "pushy" — include many trigger phrases so the skill
  activates when needed. Also include phrases for when it should NOT trigger
  if there are common near-misses.
- `license`: optional. Use if the skill will be shared.
- `compatibility`: optional. Only if the skill needs specific tools.
- `metadata`: optional. Use for author, version, team.

**Body rules:**
- Keep under 500 lines. If approaching this, split into references/ files.
- Use imperative form ("Parse the input", "Generate the report").
- Explain WHY, not just WHAT. Models respond better to reasoning than rigid
  rules. If you find yourself writing ALWAYS or NEVER in caps, reframe it as
  an explanation of why the behavior matters.
- Include 2-3 concrete examples showing input → output.
- Define the output format explicitly with a template.

**Structure the body as:**
```markdown
# Skill Name

## Purpose
One paragraph explaining what this skill does and why it matters.

## Process
Numbered steps the agent follows. Keep to 4-7 steps.

## Output Format
The exact template for the output. Use markdown structure.

## Examples
2-3 examples showing realistic input → expected output.

## Edge Cases
How to handle ambiguous, empty, or malformed inputs.
```

**Progressive disclosure:**
- Level 1: name + description (~100 words) → always loaded for all skills
- Level 2: SKILL.md body (<500 lines) → loaded when skill triggers
- Level 3: scripts/, references/, assets/ → loaded only when needed

If the skill needs domain-specific reference material (framework docs,
team conventions, templates), put it in references/ and point to it
from the SKILL.md body with clear guidance on when to read it.

### Deliverable 2: trigger-eval.json

Create 20 evaluation queries for testing the skill's description accuracy.
This file is used to optimize triggering — ensuring the skill activates
when it should and stays quiet when it shouldn't.

**Format:**
```json
[
  {"query": "realistic user prompt", "should_trigger": true},
  {"query": "realistic near-miss prompt", "should_trigger": false}
]
```

**Rules for writing eval queries:**
- 10 should-trigger + 10 should-NOT-trigger
- Make them realistic — messy, casual, with typos, personal context,
  file paths, abbreviations. Not clean academic prompts.
- Should-trigger queries: vary the phrasing. Include cases where the
  user doesn't name the skill but clearly needs it. Mix formal and
  casual. Include uncommon use cases.
- Should-NOT-trigger queries: these are the TRICKY near-misses. They
  share keywords with the skill but actually need something different.
  "Write a fibonacci function" as a negative for a testing skill is
  too easy. "Help me debug this flaky test" is a good near-miss
  because it shares the word "test" but needs debugging, not test
  case generation.

**Bad examples:**
```json
{"query": "Create test cases", "should_trigger": true}
{"query": "What's the weather?", "should_trigger": false}
```

**Good examples:**
```json
{"query": "ok so we just got this new user story for the checkout flow refactor — JIRA-4521. can you generate the full set of test cases? we use playwright btw", "should_trigger": true}
{"query": "this test keeps failing intermittently on CI, can you help me figure out why? here's the error: TimeoutError at checkout.spec.ts:47", "should_trigger": false}
```

### Deliverable 3: test-prompts.json

Create 3-5 realistic test prompts to validate the skill's actual output
quality. These are used to test the skill in Antigravity — you type the
prompt, see what the skill produces, and evaluate.

**Format:**
```json
{
  "skill_name": "test-case-generator",
  "test_prompts": [
    {
      "id": 1,
      "name": "descriptive-name",
      "prompt": "The realistic prompt a user would type",
      "expected_output": "What good output looks like — format, key sections, quality markers",
      "evaluation_criteria": [
        "Output includes positive test cases",
        "Output includes negative/boundary cases",
        "Each test case has clear steps and expected results",
        "Output format matches the team's convention"
      ]
    }
  ]
}
```

**Rules for test prompts:**
- Use the kind of language a real team member would use.
- Include at least one simple case, one complex case, and one edge case.
- Evaluation criteria should be objectively checkable — not "output is good"
  but "output contains a section for boundary value test cases."
- If the skill produces files, describe what the file should contain.

### Deliverable 4: requirements.json

Declare the runtime dependencies needed to execute the output this skill
generates. This file is read by the project's setup script
(scripts/setup.py) to install everything automatically.

**Format:**
```json
{
  "skill": "skill-name",
  "python": ["package-name"],
  "node": ["package-name"],
  "commands": ["post-install command if needed"],
  "system": ["tool-name (install from URL)"],
  "notes": "Brief note about what these dependencies are for."
}
```

**Rules for requirements.json:**
- Only include dependencies needed to RUN the generated output, not
  dependencies needed to build or edit the skill itself.
- `python`: pip packages. Use exact package names as they appear on PyPI.
- `node`: npm packages. Use exact package names as they appear on npm.
- `commands`: post-install commands like `playwright install chromium`.
- `system`: tools that can't be installed via pip/npm and need manual
  installation (e.g., k6, Docker). Include the install URL.
- `notes`: one line explaining what the deps are for.
- If the skill produces only markdown/text output with no executable
  code, use empty arrays: `"python": [], "node": []`

**Examples:**

Skill that generates Robot Framework tests:
```json
{
  "skill": "robot-framework-tester",
  "python": [
    "robotframework",
    "robotframework-seleniumlibrary",
    "robotframework-requests",
    "pabot"
  ],
  "node": [],
  "commands": [],
  "notes": "Core Robot Framework stack for running generated .robot files."
}
```

Skill that generates Lighthouse audit scripts:
```json
{
  "skill": "lighthouse-auditor",
  "python": ["robotframework", "playwright"],
  "node": ["lighthouse", "@lhci/cli", "puppeteer"],
  "commands": ["playwright install chromium"],
  "notes": "Node.js for Lighthouse CLI. Playwright for authenticated audits."
}
```

Skill that produces only markdown (no runtime deps):
```json
{
  "skill": "test-case-generator",
  "python": [],
  "node": [],
  "commands": [],
  "notes": "No runtime dependencies. Produces markdown output only."
}
```

---

## Step 4: Review with the User

Present all four deliverables and ask:

"Here's what I've created:
1. **SKILL.md** - [brief summary of what it does]
2. **trigger-eval.json** - 20 queries to test triggering accuracy
3. **test-prompts.json** - [N] test prompts to validate output quality
4. **requirements.json** - runtime dependencies for generated output

Want to review each one, or should we go straight to testing?"

Give the user a chance to adjust before proceeding. Common feedback:
- "The description is missing [trigger phrase]" → update description
- "Add a test case for [scenario]" → add to test-prompts.json
- "This near-miss should actually trigger" → flip it in trigger-eval.json

---

## Step 5: Validate with Agent Skills CLI

Guide the user to run the quality gate:

```bash
# Validate structure against agentskills.io spec
skills validate ./skill-name

# Score quality (aim for 70+)
skills score ./skill-name --verbose

# Check for conflicts with existing skills
skills sandbox ./skill-name
```

If validation fails, fix the issues and re-validate. Common fixes:
- Name has uppercase → lowercase it
- Description over 1024 chars → trim, move detail to body
- Body over 500 lines → split into references/
- Unknown frontmatter field → remove or move to metadata

---

## Step 6: Test in Antigravity

Guide the user through testing:

```bash
# Sync the skill to Antigravity
skills install ./skill-name -a antigravity
```

Then test each prompt from test-prompts.json:
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
| #3     | No        | N/A           | Description needs Z |
```

---

## Step 7: Iterate

Based on test results, improve the skill:

1. **Triggering issues** → update the description in SKILL.md frontmatter.
   Add missing trigger phrases. Remove overly broad phrases that cause
   false positives.

2. **Output quality issues** → update the body instructions. Add examples
   showing the correct behavior. Explain WHY the output should look a
   certain way.

3. **Missing edge cases** → add them to the process steps and examples.

4. **Repeated work** → if the agent keeps writing the same helper code
   during testing, bundle it in scripts/ and reference it from the body.

After improving, re-run validation and re-test:
```bash
skills validate ./skill-name
skills score ./skill-name --verbose
```

Then re-test the prompts in Antigravity. Repeat until:
- The user says it's good
- All test prompts produce acceptable output
- Score is 70+

---

## Step 8: Ship

```bash
# Final validation pass
skills validate ./skill-name
skills score ./skill-name --verbose

# Commit to the project repo
cp -r ./skill-name .agent/skills/
git add .agent/skills/skill-name/
git commit -m "feat: add skill-name skill"
git push
```

The team gets the skill on their next git pull. Antigravity picks it up
automatically from .agent/skills/.

---

## Improving an Existing Skill

If the user wants to improve a skill, not create a new one:

1. Read the existing SKILL.md
2. Ask what's not working — triggering issues? output quality? missing cases?
3. If there's no trigger-eval.json, create one (it's likely the first thing
   needed if triggering is the problem)
4. If there's no test-prompts.json, create one
5. Make improvements and follow Steps 5-8

Preserve the original name. Never rename a skill during improvement —
it breaks existing references and team habits.

---

## Quick Reference: Deliverable Checklist

Before presenting to the user, verify:

**SKILL.md:**
- [ ] name: lowercase, hyphens, ≤64 chars, matches directory name
- [ ] description: ≤1024 chars, includes trigger phrases, explains what + when
- [ ] Body: ≤500 lines, has Purpose/Process/Output Format/Examples/Edge Cases
- [ ] Examples: 2-3 realistic input → output pairs
- [ ] Output format: explicit template defined
- [ ] Instructions use imperative form and explain the "why"

**trigger-eval.json:**
- [ ] 20 queries total (10 should-trigger, 10 should-not-trigger)
- [ ] Queries are realistic, messy, varied in length and formality
- [ ] Should-not-trigger queries are genuine near-misses, not obvious irrelevant
- [ ] No duplicate intent across queries

**test-prompts.json:**
- [ ] 3-5 prompts covering simple, complex, and edge cases
- [ ] Each has a descriptive name
- [ ] Each has objectively checkable evaluation_criteria
- [ ] Prompts use real-world language, not clean academic phrasing

**requirements.json:**
- [ ] Lists only runtime dependencies (not build-time)
- [ ] Python packages use exact PyPI names
- [ ] Node packages use exact npm names
- [ ] Post-install commands listed in "commands" array
- [ ] System dependencies include install URLs
- [ ] Empty arrays for skills with no runtime deps (not omitted)
