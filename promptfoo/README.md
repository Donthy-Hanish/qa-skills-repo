# Promptfoo Integration

Run skill evals using [promptfoo](https://promptfoo.dev), the industry-standard LLM evaluation framework.

## Setup

```powershell
npm install -g promptfoo
```

## Run the eval

```powershell
cd promptfoo
$env:ANTHROPIC_API_KEY = "your-key"
promptfoo eval
```

## View results

```powershell
promptfoo view
```

This opens a web UI showing a comparison matrix: with-skill vs without-skill across all test cases, with per-assertion pass/fail and evidence.

## How it works

The `promptfooconfig.yaml` defines two providers pointing to the same model (Claude Sonnet 4.6):

- **with-skill** - loads SKILL.md as system context
- **without-skill** - bare prompt, no skill

Each test case runs against both providers. Assertions use `llm-rubric` type, which means promptfoo asks a judge model to evaluate whether each assertion is satisfied.

## Customizing

To add a new skill eval, copy the test block pattern and update the query and assertions:

```yaml
  - description: "Your test description"
    vars:
      query: "Your test prompt"
      skill_content: file://path/to/SKILL.md
    assert:
      - type: llm-rubric
        value: "Your assertion"
```

## Cost

Approximately $0.10-0.15 per full eval run (5 evals x 2 providers x assertions judged).
