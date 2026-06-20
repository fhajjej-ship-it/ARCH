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
SKILL_PATH = ROOT / "arch" / "SKILL.md"
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
    issues: list[str] = []
    first_question = scenario.get("expected_first_question")
    if not isinstance(first_question, dict):
        return ["expected_first_question must be an object"]

    options = first_question.get("options")
    if not isinstance(options, list) or len(options) != 3:
        return ["expected_first_question.options must contain exactly 3 options"]

    expected_labels = ["Recommended", "Second option", "Other"]
    labels = [option.get("label") for option in options if isinstance(option, dict)]
    if labels != expected_labels:
        issues.append(f"option labels must be {expected_labels}, got {labels}")

    for index, option in enumerate(options, start=1):
        if not isinstance(option, dict):
            issues.append(f"option {index} must be an object")
            continue
        if not str(option.get("text", "")).strip():
            issues.append(f"option {index} must include text")

    if not str(first_question.get("question", "")).strip():
        issues.append("expected_first_question.question is required")
    if not str(first_question.get("why_recommended", "")).strip():
        issues.append("expected_first_question.why_recommended is required")

    return issues


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


def validate_skill_contract() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    required_phrases = [
        "Give exactly three answer options",
        "Make option 1 the recommended default",
        "Make option 2 the strongest reasonable alternative",
        "Make option 3 `Other`",
        "Reply with 1, 2, or 3",
        "After each confirmed decision, update the relevant context file",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in skill_text]
    if missing:
        fail(f"ARCH skill missing eval-required behavior: {', '.join(missing)}")
    ok("Skill contract supports 3-option interview and context writes")


def evaluate() -> dict[str, Any]:
    validate_skill_contract()
    scenarios = load_json(SCENARIOS_PATH)
    require(isinstance(scenarios, list), "docs/evals/scenarios.json must be a list")
    require(len(scenarios) >= 7, "At least 7 eval scenarios are required")

    results = [validate_scenario(scenario) for scenario in scenarios]
    categories = {str(scenario.get("category")) for scenario in scenarios}
    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        fail(f"Missing required scenario categories: {missing_categories}")

    failures = [result for result in results if result["issues"]]
    summary = {
        "version": VERSION_PATH.read_text(encoding="utf-8").strip(),
        "generated_at": datetime.now(UTC).isoformat(),
        "scenario_count": len(scenarios),
        "passed": len(failures) == 0,
        "score": round(sum(result["score"] for result in results) / len(results), 3),
        "results": results,
    }

    for result in results:
        if result["issues"]:
            print(f"[FAIL] {result['id']}:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        else:
            print(f"[OK] {result['id']}")

    if failures:
        fail(f"{len(failures)} scenario(s) failed")
    ok(f"ARCH evals passed: {len(results)} scenarios, score {summary['score']}")
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
