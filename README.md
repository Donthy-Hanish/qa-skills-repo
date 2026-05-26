# QA Skills Repository

A collection of AI skills for Quality Assurance, built for Antigravity and validated with Agent Skills CLI.

## Quick Start

### 1. Clone and open in Antigravity
```bash
git clone <your-repo-url>
cd qa-skills-repo
# Open this folder in Antigravity
```

### 2. Install Agent Skills CLI
```bash
npm install -g agent-skills-cli
skills info  # Verify installation
```

### 3. Start building skills
In Antigravity, type:
```
Help me build a skill for generating test cases from user stories
```
The skill-creator (already installed in .agent/skills/) will guide the process.

## Project Structure

```
qa-skills-repo/
├── .agent/
│   └── skills/                    <- Antigravity reads skills from here
│       ├── skill-creator/         <- Meta-skill: teaches agent to build skills
│       │   └── SKILL.md
│       └── .templates/            <- Starter templates for new skills
│           ├── trigger-eval.template.json
│           └── test-prompts.template.json
├── docs/
│   └── playbook.md                <- Full workflow guide
├── .gitignore
└── README.md
```

## How to Build a New Skill

### Step 1: Build (in Antigravity)
Tell the agent what you need. It produces three files:
- SKILL.md (the skill itself)
- evals/trigger-eval.json (20 queries for triggering accuracy)
- evals/test-prompts.json (3-5 prompts for output quality)

### Step 2: Validate (in terminal)
```bash
skills validate .agent/skills/<skill-name>
skills score .agent/skills/<skill-name> --verbose   # Aim for 70+
skills test .agent/skills/<skill-name>
skills sandbox .agent/skills/<skill-name>            # Check conflicts
```

### Step 3: Test (in Antigravity)
Type the test prompts from test-prompts.json. Check:
- Does the skill trigger?
- Is the output useful?
- Does it stay quiet for near-miss prompts?

### Step 4: Ship
```bash
git add .agent/skills/<skill-name>/
git commit -m "feat(skills): add <skill-name>"
git push
```
Team gets the skill on their next `git pull`.

## Skills Roadmap

| Phase | Skill | Status |
|-------|-------|--------|
| 1 | test-case-generator | Planned |
| 1 | bug-report-writer | Planned |
| 1 | failure-triage-assistant | Planned |
| 2 | bdd-gherkin-writer | Planned |
| 2 | yaml-test-scaffolder | Planned |
| 2 | change-impact-analyzer | Planned |
| 3 | coverage-gap-analyzer | Planned |
| 3 | flaky-test-detector | Planned |
| 3 | test-summary-report-generator | Planned |

## Quality Standards

- All skills must pass `skills validate` before merge
- Minimum score: 70/100 on `skills score`
- Every skill ships with trigger-eval.json (20 queries) and test-prompts.json (3-5 prompts)
- No skill over 500 lines in SKILL.md body

## Docs

- [Full Playbook](docs/playbook.md) - Detailed workflow, folder structure, example flow, CI setup
