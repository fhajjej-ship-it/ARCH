#!/usr/bin/env python3
"""Evaluate ARCH scenario coverage and interview/context-writing contracts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = ROOT / "docs" / "evals" / "scenarios.json"
TRANSCRIPTS_PATH = ROOT / "docs" / "evals" / "golden-transcripts.json"
LIVE_FORWARD_TESTS_PATH = ROOT / "docs" / "evals" / "live-forward-tests.md"
SKILL_PATH = ROOT / "arch" / "SKILL.md"
QUESTION_PACK_PATH = ROOT / "arch" / "references" / "architect-question-packs.md"
VERSION_PATH = ROOT / "VERSION"
REQUIRED_CORE_CONTEXT = {
    "context/project-overview.md",
    "context/architecture-context.md",
    "context/progress-tracker.md",
}
REQUIRED_CATEGORIES = {
    "new_web_app",
    "ai_product",
    "existing_repo",
    "cli_tool",
    "mobile",
    "ops_tool",
    "regulated_risk",
}


def validate_three_option_question(question: dict[str, Any], label: str) -> list[str]:
    issues: list[str] = []

    text = str(question.get("question", "")).strip()
    if not text:
        issues.append(f"{label}.question is required")
    if text.count("?") != 1:
        issues.append(f"{label}.question must contain exactly one question mark")

    options = question.get("options")
    if not isinstance(options, list) or len(options) != 3:
        return issues + [f"{label}.options must contain exactly 3 options"]

    expected_labels = ["Recommended", "Second option", "Other"]
    option_labels = [option.get("label") for option in options if isinstance(option, dict)]
    if option_labels != expected_labels:
        issues.append(f"{label}.options labels must be {expected_labels}, got {option_labels}")

    for index, option in enumerate(options, start=1):
        if not isinstance(option, dict):
            issues.append(f"{label}.options[{index}] must be an object")
            continue
        option_text = str(option.get("text", "")).strip()
        if not option_text:
            issues.append(f"{label}.options[{index}] must include text")

    if not str(question.get("why_recommended", "")).strip():
        issues.append(f"{label}.why_recommended is required")

    if not str(question.get("architecture_impact", "")).strip():
        issues.append(f"{label}.architecture_impact is required")

    return issues


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def load_json(path: Path) -> Any:
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_output_path(path: Path) -> Path:
    output_path = path.expanduser()
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    resolved = output_path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        fail(f"Refusing to write outside repository: {resolved}")
    return resolved


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_option_shape(scenario: dict[str, Any]) -> list[str]:
    first_question = scenario.get("expected_first_question")
    if not isinstance(first_question, dict):
        return ["expected_first_question must be an object"]
    return validate_three_option_question(first_question, "expected_first_question")


def validate_context_expectations(scenario: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    expectations = scenario.get("context_expectations")
    if not isinstance(expectations, dict) or not expectations:
        return ["context_expectations must be a non-empty object"]

    expected_files = set(expectations)
    missing_core = REQUIRED_CORE_CONTEXT - expected_files
    if missing_core:
        issues.append(f"context_expectations missing core files: {sorted(missing_core)}")

    if not any(path.startswith("context/feature-specs/") for path in expected_files):
        issues.append("context_expectations must include at least one feature spec")

    for path, terms in expectations.items():
        if not path.startswith("context/") or not path.endswith(".md"):
            issues.append(f"context expectation path must be a context markdown file: {path}")
        if not isinstance(terms, list) or not all(str(term).strip() for term in terms):
            issues.append(f"context expectation for {path} must list expected terms")

    return issues


def validate_answer_flow(scenario: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    flow = scenario.get("confirmed_answer_flow")
    if not isinstance(flow, list) or not flow:
        return ["confirmed_answer_flow must contain at least one answer"]

    valid_numeric_answer_seen = False
    for index, step in enumerate(flow, start=1):
        if not isinstance(step, dict):
            issues.append(f"confirmed_answer_flow[{index}] must be an object")
            continue
        answer = str(step.get("answer", "")).strip()
        decision = str(step.get("decision", "")).strip()
        if answer in {"1", "2"} or answer.startswith("3"):
            valid_numeric_answer_seen = True
        if not decision:
            issues.append(f"confirmed_answer_flow[{index}] missing decision")

    if not valid_numeric_answer_seen:
        issues.append("confirmed_answer_flow must include a numeric 1/2/3-style answer")
    return issues


def validate_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    required_strings = ["id", "category", "title", "repo_state", "prompt"]
    for key in required_strings:
        if not str(scenario.get(key, "")).strip():
            issues.append(f"{key} is required")

    scenario_id = str(scenario.get("id", ""))
    if scenario_id and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", scenario_id):
        issues.append("id must be kebab-case")

    issues.extend(validate_option_shape(scenario))
    issues.extend(validate_context_expectations(scenario))
    issues.extend(validate_answer_flow(scenario))

    red_flags = scenario.get("red_flags")
    if not isinstance(red_flags, list) or len(red_flags) < 2:
        issues.append("red_flags must include at least 2 items")

    score = 1.0 if not issues else 0.0
    return {
        "id": scenario.get("id"),
        "category": scenario.get("category"),
        "score": score,
        "issues": issues,
    }


def validate_context_update(update: dict[str, Any], label: str) -> list[str]:
    issues: list[str] = []
    path = str(update.get("path", "")).strip()
    if not path.startswith("context/") or not path.endswith(".md"):
        issues.append(f"{label}.path must be a context markdown path")
    if not str(update.get("summary", "")).strip():
        issues.append(f"{label}.summary is required")
    return issues


def validate_golden_transcript(
    transcript: dict[str, Any],
    scenario_ids: set[str],
) -> dict[str, Any]:
    issues: list[str] = []
    required_strings = ["id", "scenario_id", "category", "title", "repo_state", "prompt"]
    for key in required_strings:
        if not str(transcript.get(key, "")).strip():
            issues.append(f"{key} is required")

    transcript_id = str(transcript.get("id", ""))
    if transcript_id and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", transcript_id):
        issues.append("id must be kebab-case")

    scenario_id = str(transcript.get("scenario_id", ""))
    if scenario_id and scenario_id not in scenario_ids:
        issues.append(f"scenario_id does not match scenarios.json: {scenario_id}")

    turns = transcript.get("turns")
    if not isinstance(turns, list) or len(turns) < 5:
        issues.append("turns must contain at least 5 turns")
        turns = []

    question_count = 0
    decision_update_count = 0
    user_answer_count = 0

    for index, turn in enumerate(turns):
        label = f"turns[{index}]"
        if not isinstance(turn, dict):
            issues.append(f"{label} must be an object")
            continue

        role = turn.get("role")
        kind = turn.get("kind")

        if role == "assistant" and kind == "question":
            question_count += 1
            if turn.get("expected_pause") is not True:
                issues.append(f"{label}.expected_pause must be true")
            if not str(turn.get("repo_inspection", "")).strip():
                issues.append(f"{label}.repo_inspection is required")
            issues.extend(validate_three_option_question(turn, label))
            continue

        if role == "user":
            user_answer_count += 1
            answer = str(turn.get("answer", "")).strip()
            if not (answer in {"1", "2"} or answer.startswith("3")):
                issues.append(f"{label}.answer must be 1, 2, or 3-style")
            if index + 1 >= len(turns):
                issues.append(f"{label} must be followed by a decision_update turn")
            else:
                next_turn = turns[index + 1]
                if not isinstance(next_turn, dict) or next_turn.get("kind") != "decision_update":
                    issues.append(f"{label} must be followed by a decision_update turn")
            continue

        if role == "assistant" and kind == "decision_update":
            decision_update_count += 1
            if not str(turn.get("confirmed_decision", "")).strip():
                issues.append(f"{label}.confirmed_decision is required")
            updates = turn.get("context_updates")
            if not isinstance(updates, list) or not updates:
                issues.append(f"{label}.context_updates must be a non-empty list")
            else:
                for update_index, update in enumerate(updates):
                    if not isinstance(update, dict):
                        issues.append(f"{label}.context_updates[{update_index}] must be an object")
                    else:
                        issues.extend(
                            validate_context_update(
                                update,
                                f"{label}.context_updates[{update_index}]",
                            )
                        )
            next_question = turn.get("next_question")
            if isinstance(next_question, dict):
                question_count += 1
                issues.extend(validate_three_option_question(next_question, f"{label}.next_question"))
            else:
                issues.append(f"{label}.next_question is required")
            continue

        issues.append(f"{label} must be an assistant question, user answer, or assistant decision_update")

    if question_count < 3:
        issues.append("transcript must include at least 3 question objects")
    if user_answer_count < 2:
        issues.append("transcript must include at least 2 user answers")
    if decision_update_count != user_answer_count:
        issues.append("each user answer must have exactly one decision_update")

    expectations = transcript.get("context_expectations")
    if not isinstance(expectations, dict) or not expectations:
        issues.append("context_expectations must be a non-empty object")
    else:
        for path, terms in expectations.items():
            if not str(path).startswith("context/") or not str(path).endswith(".md"):
                issues.append(f"context expectation path must be a context markdown file: {path}")
            if not isinstance(terms, list) or not all(str(term).strip() for term in terms):
                issues.append(f"context expectation for {path} must list expected terms")

    red_flags_absent = transcript.get("red_flags_absent")
    if not isinstance(red_flags_absent, list) or len(red_flags_absent) < 2:
        issues.append("red_flags_absent must include at least 2 items")

    score = 1.0 if not issues else 0.0
    return {
        "id": transcript.get("id"),
        "scenario_id": transcript.get("scenario_id"),
        "score": score,
        "issues": issues,
    }


def validate_skill_contract() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    required_phrases = [
        "Give exactly three answer options",
        "Make option 1 the recommended default",
        "Make option 2 the strongest reasonable alternative",
        "Make option 3 `Other`",
        "Architect Question Contract",
        "Every question must lock one architecture decision",
        "Read `references/architect-question-packs.md`",
        "Domain model and source of truth",
        "Auth and permission boundaries",
        "First buildable vertical slice",
        "**Architecture impact**",
        "Use this compact question layout",
        "**1. Recommended**",
        "**2. Second option**",
        "**3. Other**",
        "**Reply:** `1`, `2`, or `3`",
        "Put each option label on its own bold line",
        "Do not use tables for question options",
        "After each confirmed decision, update the relevant context file",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in skill_text]
    if missing:
        fail(f"ARCH skill missing eval-required behavior: {', '.join(missing)}")

    question_pack = QUESTION_PACK_PATH.read_text(encoding="utf-8")
    required_pack_phrases = [
        "## New Web App",
        "## Mobile App",
        "## AI Product",
        "## CLI Or Developer Tool",
        "## Existing Repo Rescue",
        "## Internal Ops Tool",
        "## Regulated Or Security-Sensitive App",
        "source of truth",
        "trust boundary",
        "vertical slice",
    ]
    missing_pack = [phrase for phrase in required_pack_phrases if phrase not in question_pack]
    if missing_pack:
        fail(f"ARCH question pack missing eval-required behavior: {', '.join(missing_pack)}")
    ok("Skill contract supports architect-grade 3-option interview and context writes")


def validate_live_forward_tests() -> int:
    if not LIVE_FORWARD_TESTS_PATH.exists():
        fail(f"Missing required file: {LIVE_FORWARD_TESTS_PATH.relative_to(ROOT)}")
    live_tests = LIVE_FORWARD_TESTS_PATH.read_text(encoding="utf-8")
    test_ids = re.findall(r"^## LFT-\d{2} ", live_tests, flags=re.MULTILINE)
    require(len(test_ids) >= 5, "live-forward-tests.md must include at least 5 LFT scenarios")
    required_phrases = [
        "Scoring Rubric",
        "One-question flow",
        "Architecture depth",
        "Architecture impact",
        "Context write-through",
        "MVP discipline",
        "Real Summer App Dogfood",
        "Release Decision",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in live_tests]
    if missing:
        fail(f"live-forward-tests.md missing required phrase(s): {', '.join(missing)}")
    ok(f"Live forward-test pack is present: {len(test_ids)} scenarios")
    return len(test_ids)


def evaluate() -> dict[str, Any]:
    validate_skill_contract()
    live_forward_test_count = validate_live_forward_tests()
    scenarios = load_json(SCENARIOS_PATH)
    require(isinstance(scenarios, list), "docs/evals/scenarios.json must be a list")
    require(len(scenarios) >= 7, "At least 7 eval scenarios are required")
    transcripts = load_json(TRANSCRIPTS_PATH)
    require(isinstance(transcripts, list), "docs/evals/golden-transcripts.json must be a list")
    require(len(transcripts) >= 3, "At least 3 golden transcripts are required")

    results = [validate_scenario(scenario) for scenario in scenarios]
    scenario_ids = {str(scenario.get("id")) for scenario in scenarios}
    transcript_results = [
        validate_golden_transcript(transcript, scenario_ids) for transcript in transcripts
    ]
    categories = {str(scenario.get("category")) for scenario in scenarios}
    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        fail(f"Missing required scenario categories: {missing_categories}")

    failures = [result for result in results if result["issues"]]
    transcript_failures = [result for result in transcript_results if result["issues"]]
    combined_results = results + transcript_results
    summary = {
        "version": VERSION_PATH.read_text(encoding="utf-8").strip(),
        "generated_at": datetime.now(UTC).isoformat(),
        "scenario_count": len(scenarios),
        "golden_transcript_count": len(transcripts),
        "live_forward_test_count": live_forward_test_count,
        "passed": len(failures) == 0 and len(transcript_failures) == 0,
        "score": round(
            sum(result["score"] for result in combined_results) / len(combined_results),
            3,
        ),
        "results": results,
        "golden_transcript_results": transcript_results,
    }

    for result in results:
        if result["issues"]:
            print(f"[FAIL] {result['id']}:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        else:
            print(f"[OK] {result['id']}")

    for result in transcript_results:
        if result["issues"]:
            print(f"[FAIL] {result['id']}:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        else:
            print(f"[OK] {result['id']}")

    if failures:
        fail(f"{len(failures)} scenario(s) failed")
    if transcript_failures:
        fail(f"{len(transcript_failures)} golden transcript(s) failed")
    ok(
        "ARCH evals passed: "
        f"{len(results)} scenarios, "
        f"{len(transcript_results)} golden transcripts, "
        f"score {summary['score']}"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate ARCH scenario coverage.")
    parser.add_argument(
        "--write-baseline",
        type=Path,
        help="Write eval results JSON to this path.",
    )
    args = parser.parse_args()

    summary = evaluate()
    if args.write_baseline:
        output_path = resolve_repo_output_path(args.write_baseline)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        ok(f"Wrote baseline: {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
