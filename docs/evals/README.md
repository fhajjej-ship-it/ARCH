# ARCH Eval Pack

This eval pack checks whether ARCH keeps its core promise across realistic project starts:

- ask one decision at a time
- make the question easy to answer with exactly three options
- make every question lock an architecture boundary, source of truth, trust boundary, failure mode, or vertical slice
- keep question output scannable with bold block labels instead of inline walls of text
- explain the architecture impact of each decision
- recommend a strong default
- record confirmed answers into `context/`
- preserve MVP discipline instead of over-architecting

## Run

```bash
python3 scripts/evaluate_arch.py
```

This is a static eval. It validates the scenario catalog, the expected 3-option interview shape, context-writing expectations, the live forward-test pack, and the installed skill instructions. It does not call a model.

## Golden Transcripts

`golden-transcripts.json` contains ideal short ARCH conversations for representative project starts. These are not generated at test time. They are reviewable fixtures that lock the expected behavior:

- inspect the repo before asking
- ask one decision question at a time
- give exactly three answer options
- format each option as a separate bold-labeled block
- include an `architecture_impact` for every question object
- wait for the developer's answer
- turn each confirmed answer into concrete `context/` updates
- ask the next single question only after recording the decision

The evaluator checks the transcript structure and fails the release if a golden transcript drifts away from that contract.

## Live Forward Tests

`live-forward-tests.md` contains manual tests for fresh Codex sessions using the installed `$arch` skill. Use it when changing interview behavior because static fixtures cannot prove that a real run feels architect-level.

The live pack covers:

- empty new app
- existing repo rescue
- AI product
- mobile app
- regulated-risk app
- real Summer app dogfood

Live tests should not receive the expected answers or rubric during the run.

## Scenario Workflow

For manual forward testing:

1. Create a temporary empty repo or use the described repo state.
2. Start Codex and run the scenario prompt.
3. Confirm the recommended answer with `1` unless the scenario says otherwise.
4. Check that ARCH creates or updates `context/` after enough decisions exist.
5. Score the result against the rubric below.

For release candidates that change interview behavior, use `live-forward-tests.md` instead of only this short workflow.

## Rubric

Score each scenario from 0-2 on each dimension:

- **Question shape**: one question only, exactly three options, option 1 recommended, option 2 plausible, option 3 other, with each option label on its own bold line.
- **Architecture depth**: every question decides a boundary, source of truth, trust boundary, failure mode, or first vertical slice and explains what context files will change.
- **Recommendation quality**: default is narrow, modern, pragmatic, and appropriate for v1.
- **Context writing**: confirmed decisions are written to the right `context/` files.
- **MVP discipline**: cuts unnecessary scope and avoids premature architecture.
- **Agent handoff**: resulting feature specs and workflow rules are executable by a coding assistant.

Passing bar:

- No dimension scores 0.
- Average score is at least 1.6.
- No critical red flags from the scenario are present.

## Updating The Pack

Add a scenario when ARCH fails in a new way. Keep scenarios realistic and short. Each scenario should include:

- initial repo state
- user prompt
- expected first question with 3 options
- architecture impact of the question
- confirmed answer flow
- expected context updates
- red flags

Add a golden transcript when a scenario needs a concrete example of ideal assistant behavior. Keep transcripts short, focused, and tied to a `scenario_id` in `scenarios.json`.
