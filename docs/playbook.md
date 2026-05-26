# QA Skills: Discovery, Community Resources & Creation Playbook

---

## Part 1: Where to Find Existing QA Skills

The skills ecosystem has grown significantly. Here are the key places to discover what QA teams are already using.

---

### Dedicated QA Skills Platforms

**QASkills.sh** — qaskills.sh
The most focused resource. A curated collection of QA-specific skills covering unit testing, E2E, BDD, test data generation, API testing, and more. It lists skills compatible with 30+ AI coding agents including Claude Code, Codex, Cursor, and Antigravity. Their blog (qaskills.sh/blog) also publishes "must-have" skill roundups specifically for QA.

**Key QA skills available there:**
- Playwright E2E testing
- Jest/Mocha unit testing
- Python BDD with Behave/Gherkin
- Test data generation with Faker
- API simulation with WireMock
- Code review & quality assurance
- Prompt testing & LLM output evaluation

---

### General Skills Marketplaces (with QA categories)

**SkillsMP** — skillsmp.com
Search 1.2M+ agent skills with filtering by occupation. Has a Testing & QA category. Quality-filtered (minimum 2 GitHub stars). Compatible with Claude Code, Codex CLI, and ChatGPT.

**Claude Marketplaces** — claudemarketplaces.com
6,700+ skills with a dedicated "Testing & QA" category. Browse at claudemarketplaces.com/skills/category/testing. Updated daily from GitHub.

**ClaudeSkills.info** — claudeskills.info
Organized by use case. Has a "Testing" category with 9 skills covering unit tests, E2E testing, and code quality. Also lists 83 development skills that overlap with QA automation.

**Agensi.io** — agensi.io/skills/testing-qa
Curated by install count and community votes. Top QA skills include code-reviewer (116 installs), api-contract-tester, lobster-debugging, and data-faker.

**MCP Market** — mcpmarket.com
Lists specific QA personas like "QA Expert" (automated test suite creation with test pyramid approach) and "QA Engineer" (80%+ coverage enforcement, edge case detection, bug report generation).

**Awesome Skills** — awesomeskill.ai/category/testing-qa
Community-curated with exploratory testing, accessibility checking, and React code quality skills.

---

### GitHub Repositories (curated lists)

**Anthropic Official** — github.com/anthropics/skills
The canonical source. Contains example skills and the skill format standard. Document skills (docx, pdf, pptx, xlsx) are included as reference for complex production skills.

**Awesome Claude Skills (TravisVN)** — github.com/travisvn/awesome-claude-skills
Community-curated list including obra/superpowers (20+ battle-tested skills for TDD, debugging, collaboration).

**ComposioHQ** — github.com/ComposioHQ/awesome-claude-skills
1000+ production-ready skills. Organized by use case with detailed installation instructions.

**alirezarezvani/claude-skills** — github.com/alirezarezvani/claude-skills
313+ skills across engineering, product, and operations. All ~402 Python tools run without pip installs.

**obviousworks** — github.com/obviousworks/Claude-AI-skills-collection-2026
Both official and community-built skills organized by category.

---

### In Claude Code Itself

If your team is using Claude Code (or will be via Antigravity), you can discover and install skills directly from the terminal:

```
/plugin                              # Opens plugin browser
/plugin marketplace add <repo>       # Adds a marketplace
/plugin install <skill-name>         # Installs a specific skill
```

Skills install to `~/.claude/skills/` (personal) or `.claude/skills/` (project-scoped, shareable via git).

---

## Part 2: Creation & Deployment — Antigravity + Agent Skills CLI

### Tooling Stack

| Tool | Role | When |
|------|------|------|
| **Antigravity** | Build skills, test skills, use skills daily | Entire lifecycle |
| **Agent Skills CLI** | Quality gate — validate, score, test, conflict-check | Before every ship |
| **skill-creator (SKILL.md)** | Placed in .agent/skills/ — teaches Antigravity how to build skills | Phase 1 |
| **agentskills.io spec** | The standard both tools follow | Reference |

### One-Time Setup

```bash
# Install Agent Skills CLI globally
npm install -g agent-skills-cli

# Verify installation
skills info
```

---

### Project Folder Structure

```
your-project/
├── .agent/
│   └── skills/                          ← Antigravity reads skills from here
│       ├── skill-creator/               ← Meta-skill: teaches agent to build skills
│       │   └── SKILL.md
│       ├── test-case-generator/         ← QA skill #1 (you'll build this)
│       │   ├── SKILL.md
│       │   ├── evals/
│       │   │   ├── trigger-eval.json    ← 20 queries for triggering accuracy
│       │   │   └── test-prompts.json    ← 3-5 prompts for output quality
│       │   ├── scripts/                 ← Optional: helper scripts
│       │   ├── references/              ← Optional: reference docs
│       │   └── templates/               ← Optional: output templates
│       ├── bug-report-writer/           ← QA skill #2
│       │   ├── SKILL.md
│       │   └── evals/
│       │       ├── trigger-eval.json
│       │       └── test-prompts.json
│       └── failure-triage-assistant/    ← QA skill #3
│           ├── SKILL.md
│           └── evals/
│               ├── trigger-eval.json
│               └── test-prompts.json
├── src/
├── tests/
└── ...
```

The skill-creator is the first skill you place. After that, you use it
to build every other skill — it's the skill that makes skills.

---

### Example Flow: Building "test-case-generator" from Scratch

Here's the complete journey from idea to deployment, showing every
interaction with Antigravity and every Agent Skills CLI command.

---

#### Phase 1: Build (in Antigravity)

**You type in Antigravity:**
```
Help me build a skill for generating test cases from user stories.
We use Playwright for E2E and Jest for unit tests. Output should be
markdown with sections for positive, negative, boundary, and edge cases.
```

**What happens:**
The agent finds the skill-creator in .agent/skills/ and follows its
process. It asks you clarifying questions:

```
Agent: "A few questions before I draft this:
1. Do your user stories follow a specific format (Given/When/Then,
   or plain acceptance criteria)?
2. Should the test cases include automation-ready selectors or
   just human-readable steps?
3. Any naming convention for test IDs?"
```

**You answer:**
```
Plain acceptance criteria from Jira. Human-readable steps for now,
we'll automate later. No specific ID convention — just sequential.
```

**The agent produces three files:**

**File 1: .agent/skills/test-case-generator/SKILL.md**
```markdown
---
name: test-case-generator
description: >
  Generate comprehensive test cases from user stories, acceptance criteria,
  or feature descriptions. Covers positive, negative, boundary, and edge
  cases. Use when someone says "write test cases", "what should we test",
  "generate tests for this story", "create test scenarios", pastes a user
  story or acceptance criteria, or asks "what are the edge cases for this
  feature". Also trigger for "test coverage for this requirement" or
  "break this story into test cases".
---

# Test Case Generator

## Purpose
Transform user stories and acceptance criteria into structured,
comprehensive test cases that ensure nothing is missed before
development or during review.

## Process
1. Read the user story or acceptance criteria
2. Identify the core functionality being described
3. Generate positive test cases (happy path — it works as expected)
4. Generate negative test cases (invalid inputs, error handling)
5. Generate boundary test cases (limits, min/max values, empty states)
6. Generate edge cases (concurrency, timeouts, unusual combinations)
7. Format using the output template below

## Output Format

# Test Cases: [Feature/Story Name]

## Positive Cases
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| TC-001 | ... | ... | ... |

## Negative Cases
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|

## Boundary Cases
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|

## Edge Cases
| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|

## Examples

**Example 1:**
Input: "As a user, I can reset my password via email"
Output:
- TC-001 (Positive): Valid email, receives reset link, sets new password
- TC-002 (Negative): Unregistered email, shows appropriate error
- TC-003 (Boundary): Password at minimum length (8 chars)
- TC-004 (Edge): Reset link clicked after expiry (24hrs)

## Edge Cases to Always Consider
When generating test cases, think about these categories that are
commonly missed. Not all apply to every story, but scanning this
list helps catch gaps:
- Empty/null inputs
- Maximum length strings
- Special characters and unicode
- Concurrent access by multiple users
- Network timeout mid-operation
- Permission boundaries (logged out, wrong role)
- State transitions (what if the user goes back?)
```

**File 2: .agent/skills/test-case-generator/evals/trigger-eval.json**
```json
[
  {"query": "ok so we got this new story from the PM — JIRA-4521 for the checkout flow refactor. can you write up all the test cases? we use playwright", "should_trigger": true},
  {"query": "here are the acceptance criteria for the search filters feature, generate test scenarios covering all the edge cases too", "should_trigger": true},
  {"query": "what should we test for this? As a user I can upload a profile picture in jpg or png format up to 5MB", "should_trigger": true},
  {"query": "break this user story into test cases: user can apply discount codes at checkout, codes can be percentage or fixed amount", "should_trigger": true},
  {"query": "need test coverage for the new notification preferences page, here's the figma link and AC from jira", "should_trigger": true},
  {"query": "generate tests for the login flow — email/password, SSO, and forgot password paths", "should_trigger": true},
  {"query": "what are the edge cases for the payment retry logic? it tries 3 times with exponential backoff", "should_trigger": true},
  {"query": "can u create test scenarios for this API endpoint? POST /api/orders with fields: items[], shippingAddress, paymentMethod", "should_trigger": true},
  {"query": "write test cases for this requirement: users can schedule messages to be sent later, min 5 mins max 30 days", "should_trigger": true},
  {"query": "I have a Playwright test for the login flow and its super flaky — sometimes passes sometimes fails. the error is TimeoutError at login.spec.ts:47. can you help me figure out whats wrong?", "should_trigger": false},
  {"query": "review this pull request and check if theres any bugs in the validation logic", "should_trigger": false},
  {"query": "help me write a Playwright script that clicks the login button and fills in the email field", "should_trigger": false},
  {"query": "our test coverage report shows 62% for the orders module. whats the best way to improve it?", "should_trigger": false},
  {"query": "set up jest for our react project — we need the config file and a sample test", "should_trigger": false},
  {"query": "can you explain the difference between unit tests and integration tests?", "should_trigger": false},
  {"query": "triage this failure: NullPointerException at OrderService.java:142 during checkout regression run", "should_trigger": false},
  {"query": "write a bug report for this — the search filter shows 0 results when you select 'Price: High to Low' with a category filter active", "should_trigger": false},
  {"query": "help me optimize this playwright test — its taking 45 seconds because of all the waitForSelector calls", "should_trigger": false},
  {"query": "summarize the test results from last sprint — we had 342 passed 12 failed 3 skipped", "should_trigger": false}
]
```

**File 3: .agent/skills/test-case-generator/evals/test-prompts.json**
```json
{
  "skill_name": "test-case-generator",
  "test_prompts": [
    {
      "id": 1,
      "name": "simple-user-story",
      "prompt": "Write test cases for this story: As a user, I can reset my password by entering my email address and receiving a reset link.",
      "expected_output": "Structured markdown with positive, negative, boundary, and edge case sections",
      "evaluation_criteria": [
        "Contains a Positive Cases section with at least 2 cases",
        "Contains a Negative Cases section (invalid email, unregistered email)",
        "Contains a Boundary Cases section (password length limits)",
        "Contains an Edge Cases section (expired link, multiple resets)",
        "Each case has ID, Scenario, Steps, and Expected Result",
        "Cases are specific and actionable, not vague"
      ]
    },
    {
      "id": 2,
      "name": "complex-acceptance-criteria",
      "prompt": "Here are the ACs for our new discount code feature:\n- Users can enter a discount code at checkout\n- Codes can be percentage (10%, 20%) or fixed amount ($5, $10)\n- Only one code per order\n- Codes have an expiry date\n- Minimum order value may be required\n- Some codes are single-use, some are multi-use\n\nGenerate comprehensive test cases.",
      "expected_output": "Detailed test cases covering all 6 ACs with cross-cutting edge cases",
      "evaluation_criteria": [
        "Covers all 6 acceptance criteria explicitly",
        "Includes combination cases (percentage + minimum order, expired + single-use)",
        "Boundary cases for percentage (0%, 100%, >100%) and amounts ($0, negative)",
        "Edge case for applying code, removing it, then re-applying",
        "At least 15 total test cases across all sections"
      ]
    },
    {
      "id": 3,
      "name": "api-endpoint",
      "prompt": "Generate test cases for: POST /api/users with body {name: string, email: string, role: 'admin'|'user'|'viewer'}",
      "expected_output": "API-focused test cases covering request validation, auth, and response codes",
      "evaluation_criteria": [
        "Covers valid request with each role",
        "Covers missing required fields",
        "Covers invalid email format",
        "Covers invalid role value",
        "Includes auth/permission edge cases",
        "References expected HTTP status codes (201, 400, 401, 409)"
      ]
    },
    {
      "id": 4,
      "name": "vague-input",
      "prompt": "what should we test for the search feature?",
      "expected_output": "Agent asks clarifying questions OR generates common search test patterns",
      "evaluation_criteria": [
        "Either asks what kind of search (text, filters, faceted) or generates generic search patterns",
        "Does not produce empty or overly vague output",
        "If generating, covers: empty query, special characters, no results, pagination"
      ]
    }
  ]
}
```

---

#### Phase 2: Validate (Agent Skills CLI)

Now you open your terminal (or Antigravity's built-in terminal) and
run the quality gate. These are manual commands you run yourself:

```bash
# Step 1: Navigate to the skill
cd your-project/.agent/skills/test-case-generator

# Step 2: Validate structure against agentskills.io spec
skills validate .

# Expected output:
# ✔ PASS  SKILL.md
#   name: valid (lowercase, hyphens, ≤64 chars)
#   description: valid (≤1024 chars, non-empty)
#   body: 87 lines (under 500 limit)

# Step 3: Score quality (aim for 70+)
skills score . --verbose

# Expected output:
# Structure:   85/100  ✔ frontmatter complete, directory matches name
# Clarity:     80/100  ✔ clear instructions, good examples
# Specificity: 90/100  ✔ concrete output format, real examples
# Advanced:    70/100  ✔ edge cases documented
# ─────────────────────
# Overall:     82/100  Grade: B
# PASS (threshold: 70)

# Step 4: Test built-in assertions
skills test .

# Step 5: Check for conflicts with existing skills
skills sandbox .

# Expected output:
# ⚠ Potential overlap with "bdd-gherkin-writer" on trigger:
#   "write test scenarios"
# → Action: differentiate descriptions or merge skills
```

**If validation fails**, fix and re-run. Common fixes:

| Error | Fix |
|-------|-----|
| Name has uppercase | Lowercase it in frontmatter |
| Description > 1024 chars | Trim, move detail to body |
| Body > 500 lines | Split into references/ files |
| Unknown frontmatter field | Move to metadata: block or remove |
| Conflict with another skill | Differentiate description trigger phrases |

---

#### Phase 3: Test in Antigravity

```bash
# Sync the skill to Antigravity (if not already in .agent/skills/)
skills install ./test-case-generator -a antigravity
```

Now test each prompt from test-prompts.json by typing them in Antigravity:

**Test 1 — Simple user story:**
```
Write test cases for this story: As a user, I can reset my password
by entering my email address and receiving a reset link.
```
Check: Did the skill trigger? Does output have all 4 sections?
Does each case have ID, Scenario, Steps, Expected Result?

**Test 2 — Complex ACs:**
```
Here are the ACs for our new discount code feature: [paste the ACs]
Generate comprehensive test cases.
```
Check: Does it cover all 6 ACs? Are there combination/cross-cutting cases?

**Test 3 — API endpoint:**
```
Generate test cases for: POST /api/users with body
{name: string, email: string, role: 'admin'|'user'|'viewer'}
```
Check: Does it include HTTP status codes? Auth edge cases?

**Test 4 — Vague input:**
```
what should we test for the search feature?
```
Check: Does the agent ask for clarification or produce useful generic patterns?

**Track results:**

| # | Prompt | Triggered? | Quality | Notes |
|---|--------|-----------|---------|-------|
| 1 | Password reset story | ✅ Yes | Good | All 4 sections present |
| 2 | Discount code ACs | ✅ Yes | Good | 18 test cases, covers all ACs |
| 3 | API endpoint | ✅ Yes | Fix needed | Missing 409 Conflict case |
| 4 | Vague "search" | ✅ Yes | Good | Asked clarifying question |

**Also test triggering accuracy** using trigger-eval.json. Type 3-4 of the
should-NOT-trigger prompts and verify the skill stays quiet:

```
I have a Playwright test for the login flow and its super flaky —
sometimes passes sometimes fails. can you help me figure out whats wrong?
```
Expected: Skill should NOT trigger (this is debugging, not test case generation).

---

#### Phase 4: Iterate

Based on test results, go back to Antigravity:

```
The test-case-generator skill is missing 409 Conflict responses for
the API test case. Also, when I paste ACs without mentioning "test
cases" explicitly, it doesn't always trigger. Update the skill.
```

The agent reads the skill-creator, makes the improvements, and produces
updated files. Then re-validate:

```bash
skills validate .agent/skills/test-case-generator
skills score .agent/skills/test-case-generator --verbose
```

Re-test the failed prompts in Antigravity. Repeat until all tests pass.

---

#### Phase 5: Ship

```bash
# Final validation
skills validate .agent/skills/test-case-generator
skills score .agent/skills/test-case-generator --verbose
# Must be: PASS, score ≥ 70

# Commit to repo
git add .agent/skills/test-case-generator/
git commit -m "feat(skills): add test-case-generator skill

Outputs: SKILL.md + trigger-eval.json + test-prompts.json
Score: 82/100 (Grade B)
Tested: 4/4 prompts passing in Antigravity"

git push
```

The team gets the skill on their next `git pull`. Antigravity picks it up
automatically from `.agent/skills/`.

**Optional: Add CI quality gate**

```yaml
# .github/workflows/skill-quality.yml
name: Skill Quality Gate
on:
  pull_request:
    paths: ['.agent/skills/**']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '18' }
      - run: npm install -g agent-skills-cli
      - name: Validate all skills
        run: |
          for skill in .agent/skills/*/; do
            echo "Validating $skill..."
            skills validate "$skill"
            score=$(skills score "$skill" --json | jq '.score')
            if [ "$score" -lt 70 ]; then
              echo "FAIL: $skill scored $score (minimum: 70)"
              exit 1
            fi
            echo "PASS: $skill scored $score"
          done
```

Now every PR that modifies a skill gets validated automatically.

---

#### Phase 6: Maintain

- Review skill performance quarterly — are outputs still meeting quality bar?
- Update when frameworks, tools, or team conventions change
- Collect feedback from skill users (Slack thread, retro notes)
- Re-run `skills score` after updates to ensure quality doesn't regress
- Version control skills alongside code — they're part of the project

---

### Summary: The Complete Flow

```
You in Antigravity                     Terminal (Agent Skills CLI)
──────────────────                     ──────────────────────────

"Build a skill for generating          
 test cases from user stories"         
        │                              
        ▼                              
Agent follows skill-creator,           
interviews you, produces:              
  • SKILL.md                           
  • trigger-eval.json                  
  • test-prompts.json                  
        │                              
        │                              skills validate ./skill-name
        │                              skills score ./skill-name --verbose
        │                              skills test ./skill-name
        │                              skills sandbox ./skill-name
        │                                      │
        │◄─────── Fix if fails ────────────────┘
        │                              
Type test prompts,                     
review outputs,                        
check triggering accuracy              
        │                              
        │── Issues found? ──► "Update the skill to fix X"
        │                              │
        │◄─────────────────────────────┘
        │                              
        │                              skills validate (final pass)
        │                              skills score ≥ 70 ✔
        │                              
        ▼                              
git add + commit + push ───────────► CI runs skills validate + score
        │                              
        ▼                              
Team does git pull,                    
skill appears in Antigravity           
for everyone automatically             
```

---

## Part 3: Recommended First Skills for QA

Based on frequency of use and time saved, start here:

| Priority | Skill | Why First |
|----------|-------|-----------|
| 1 | test-case-generator | Used daily, saves 30-60 min per feature |
| 2 | bug-report-writer | Standardizes quality, removes busywork |
| 3 | failure-triage-assistant | Speeds up the most frustrating part of QA |
| 4 | bdd-gherkin-writer | Direct fit with SDD approach |
| 5 | yaml-test-scaffolder | Natural fit with peco-regression-suite |

Build them one at a time using the flow above. Each one ships with its
SKILL.md + trigger-eval.json + test-prompts.json, validated and scored
before the team ever sees it.
