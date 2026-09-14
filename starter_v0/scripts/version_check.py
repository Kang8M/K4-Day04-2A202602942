"""Verify that version labels, artifact hashes and run files agree.

Owned by role A (Prompt Architect). Read-only: it never edits an artifact.

A version label is only meaningful if it is tied to a specific pair of artifact
bytes. This script catches the three ways that tie can break:

  * the same label was used for two different artifacts;
  * two labels point at byte-identical artifacts (a version that never changed);
  * a run cited in version_log.csv was produced from different artifacts.

Usage:
    python scripts/version_check.py
    python scripts/version_check.py --runs-dir runs
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from versioning import build_artifact_version, file_hash, short_hash  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
SNAPSHOT_DIR = ARTIFACTS_DIR / "prompt_versions"


def load_log(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def snapshot_path(version: str) -> Path:
    return SNAPSHOT_DIR / f"{version}_system_prompt.md"


def check_log_internal(rows: list[dict[str, str]], problems: list[str]) -> None:
    """Labels and hashes must be a one-to-one mapping."""
    by_label: dict[str, set[str]] = defaultdict(set)
    by_hash: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        key = (row["prompt_hash"], row["tools_hash"])
        by_label[row["version"]].add("+".join(key))
        by_hash[key].add(row["version"])

    for label, hashes in by_label.items():
        if len(hashes) > 1:
            problems.append(f"label {label!r} maps to {len(hashes)} different artifact hashes")
    for key, labels in by_hash.items():
        if len(labels) > 1:
            joined = ", ".join(sorted(labels))
            problems.append(f"labels {joined} share artifact hash p{key[0]}+t{key[1]} — no artifact actually changed")


def check_snapshots(rows: list[dict[str, str]], tools_path: Path, problems: list[str]) -> None:
    """Every logged version must have a snapshot that still hashes the same."""
    for row in rows:
        version = row["version"]
        path = snapshot_path(version)
        if not path.exists():
            problems.append(f"{version}: missing snapshot {path.relative_to(ROOT)}")
            continue
        actual = build_artifact_version(version, path, tools_path)
        if short_hash(actual.prompt_hash) != row["prompt_hash"]:
            problems.append(
                f"{version}: snapshot prompt hash {short_hash(actual.prompt_hash)} "
                f"!= logged {row['prompt_hash']}"
            )
        if short_hash(actual.tools_hash) != row["tools_hash"]:
            problems.append(
                f"{version}: tools.yaml hash {short_hash(actual.tools_hash)} "
                f"!= logged {row['tools_hash']} — re-cut this version with role B"
            )


def check_live_prompt(rows: list[dict[str, str]], tools_path: Path, problems: list[str]) -> str | None:
    """artifacts/system_prompt.md must be byte-identical to one logged version."""
    live = ARTIFACTS_DIR / "system_prompt.md"
    live_hash = short_hash(file_hash(live))
    tools_hash = short_hash(file_hash(tools_path))
    for row in rows:
        if row["prompt_hash"] == live_hash and row["tools_hash"] == tools_hash:
            return row["version"]
    problems.append(
        f"system_prompt.md (p{live_hash}+t{tools_hash}) matches no row in version_log.csv — "
        "snapshot it and log it before running an eval"
    )
    return None


def check_runs(rows: list[dict[str, str]], runs_dir: Path, problems: list[str]) -> list[str]:
    """Runs must carry the hashes of the version they claim."""
    notes: list[str] = []
    logged = {row["version"]: (row["prompt_hash"], row["tools_hash"]) for row in rows}

    for path in sorted(runs_dir.glob("*.json")):
        try:
            run: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{path.name}: unreadable ({type(exc).__name__})")
            continue

        label = run.get("version")
        actual = (short_hash(run.get("prompt_hash", "")), short_hash(run.get("tools_hash", "")))
        expected = logged.get(label)
        if expected is None:
            notes.append(f"{path.name}: version {label!r} is not in version_log.csv")
        elif expected != actual:
            problems.append(
                f"{path.name}: labelled {label} but ran p{actual[0]}+t{actual[1]}, "
                f"while the log records p{expected[0]}+t{expected[1]}"
            )

        summary = run.get("summary", {})
        errors = summary.get("provider_error_cases")
        if errors:
            notes.append(
                f"{path.name}: {errors}/{summary.get('total_cases')} provider errors — "
                "not usable as evidence"
            )
    return notes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path, default=ARTIFACTS_DIR / "version_log.csv")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    args = parser.parse_args()

    rows = load_log(args.log)
    if not rows:
        raise SystemExit(f"No rows in {args.log}")

    problems: list[str] = []
    check_log_internal(rows, problems)
    check_snapshots(rows, args.tools, problems)
    live_version = check_live_prompt(rows, args.tools, problems)
    notes = check_runs(rows, args.runs_dir, problems) if args.runs_dir.exists() else []

    print(f"Logged versions: {', '.join(row['version'] for row in rows)}")
    print(f"Live system_prompt.md: {live_version or 'UNLOGGED'}")

    if notes:
        print("\nNotes:")
        for note in notes:
            print(f"  - {note}")

    if problems:
        print("\nFAIL:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    print("\nOK: labels, snapshots, live artifact and runs agree.")


if __name__ == "__main__":
    main()
