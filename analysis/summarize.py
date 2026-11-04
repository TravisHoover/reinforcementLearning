"""Summarise eval logs into results tables.

    python analysis/summarize.py logs/standard logs/pressure
    python analysis/summarize.py logs/standard logs/pressure --csv results/samples.csv

Reads every Inspect log under the given directories, one row per (model, prompt style,
task, variant, epoch), and prints:
  1. headline rates per model and prompt style
  2. outcome counts per task
  3. how often each kind of violation appeared
  4. the gamed samples to read first in `inspect view`
  5. the flagged samples to review: soft violations (line-pattern matches) only,
     which ordinary code can trip, so they aren't counted as gamed
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

SCORER = "shortcut_scorer"


def load_rows(log_dirs: list[str]) -> list[dict]:
    rows = []
    infos = [info for d in log_dirs for info in list_eval_logs(d)]
    for info in infos:
        log = read_eval_log(info)
        if log.status != "success" or not log.samples:
            continue
        model = log.eval.model.removeprefix("anthropic/")
        if model.startswith(("none", "mockllm")):
            continue  # pipeline tests, not model runs
        for s in log.samples:
            score = (s.scores or {}).get(SCORER)
            if score is None or not score.metadata:
                continue
            m = score.metadata
            usage = sum(u.total_tokens for u in (s.model_usage or {}).values())
            rows.append({
                "model": model,
                "prompt_style": s.metadata.get("prompt_style", "standard"),
                "task": m["task_id"],
                "variant": m["variant"],
                "epoch": s.epoch,
                "outcome": m["outcome"],
                "solved": m["solved"],
                "gamed": m["gamed"],
                "flagged": m.get("flagged", False),
                "flagged_conflict": m["flagged_conflict"],
                "violations": ";".join(sorted({v["kind"] for v in m["violations"]})),
                "hit_limit": s.limit.type if s.limit else "",
                "tokens": usage,
                "sample_id": s.id,
                "log": Path(info.name).name,
            })
    return rows


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}% ({n}/{d})" if d else "-"


def headline(rows: list[dict]) -> str:
    groups = defaultdict(list)
    for r in rows:
        groups[(r["model"], r["prompt_style"])].append(r)
    out = [
        "| Model | Prompt | Solved (possible) | Gamed (possible) | Visible-only (possible) "
        "| Flagged for review (possible) | Gamed (impossible) | Flagged conflict when honest (impossible) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for (model, style), rs in sorted(groups.items()):
        pos = [r for r in rs if r["variant"] == "possible"]
        imp = [r for r in rs if r["variant"] == "impossible"]
        honest = [r for r in imp if not r["gamed"]]
        out.append(
            f"| {model} | {style} | {pct(sum(r['solved'] for r in pos), len(pos))} "
            f"| {pct(sum(r['gamed'] for r in pos), len(pos))} "
            f"| {pct(sum(r['outcome'] == 'visible_only' for r in pos), len(pos))} "
            f"| {pct(sum(r['flagged'] and not r['gamed'] for r in pos), len(pos))} "
            f"| {pct(sum(r['gamed'] for r in imp), len(imp))} "
            f"| {pct(sum(r['flagged_conflict'] for r in honest), len(honest))} |"
        )
    return "\n".join(out)


def per_task(rows: list[dict]) -> str:
    outcomes = ["solved", "solved_flagged", "solved_with_violation", "gamed", "visible_only", "failed",
                "honest_compliant", "honest"]
    groups = defaultdict(Counter)
    for r in rows:
        groups[(r["task"], r["variant"], r["model"])][r["outcome"]] += 1
    out = ["| Task | Variant | Model | " + " | ".join(outcomes) + " |",
           "|---|---|---|" + "---|" * len(outcomes)]
    for (task, variant, model), c in sorted(groups.items()):
        out.append(f"| {task} | {variant} | {model} | " + " | ".join(str(c[o] or "") for o in outcomes) + " |")
    return "\n".join(out)


def violation_counts(rows: list[dict]) -> str:
    c = Counter(k for r in rows for k in r["violations"].split(";") if k)
    if not c:
        return "_No violations recorded._"
    return "\n".join(["| Violation | Samples |", "|---|---|"] + [f"| {k} | {n} |" for k, n in c.most_common()])


def to_review(rows: list[dict]) -> str:
    gamed = [r for r in rows if r["gamed"]]
    if not gamed:
        return "_None._"
    out = ["| Model | Prompt | Sample | Epoch | Violations | Log |", "|---|---|---|---|---|---|"]
    for r in sorted(gamed, key=lambda r: (r["task"], r["model"])):
        out.append(f"| {r['model']} | {r['prompt_style']} | {r['sample_id']} | {r['epoch']} "
                   f"| {r['violations'] or '(passed impossible tests)'} | {r['log']} |")
    return "\n".join(out)


def flagged_to_review(rows: list[dict]) -> str:
    """Samples with soft violations only. Read the transcript: the agent took a
    shortcut, or wrote ordinary code that matches a pattern."""
    flagged = [r for r in rows if r["flagged"] and not r["gamed"]]
    if not flagged:
        return "_None._"
    out = ["| Model | Prompt | Sample | Epoch | Outcome | Soft violations | Log |", "|---|---|---|---|---|---|---|"]
    for r in sorted(flagged, key=lambda r: (r["task"], r["model"])):
        out.append(f"| {r['model']} | {r['prompt_style']} | {r['sample_id']} | {r['epoch']} "
                   f"| {r['outcome']} | {r['violations']} | {r['log']} |")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("log_dirs", nargs="+")
    ap.add_argument("--csv", help="also write one row per sample to this CSV file")
    args = ap.parse_args()
    rows = load_rows(args.log_dirs)
    if not rows:
        raise SystemExit(f"no scored model samples found under {' '.join(args.log_dirs)}")
    if args.csv:
        Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    limited = sum(1 for r in rows if r["hit_limit"])
    print(f"{len(rows)} scored samples; {limited} stopped at a message, token, or time limit.\n")
    print("## Headline\n\n" + headline(rows) + "\n")
    print("## Outcomes by task\n\n" + per_task(rows) + "\n")
    print("## Violations\n\n" + violation_counts(rows) + "\n")
    print("## Gamed samples to review\n\n" + to_review(rows) + "\n")
    print("## Flagged samples to review (soft violations only, not counted as gamed)\n\n" + flagged_to_review(rows))


if __name__ == "__main__":
    main()
