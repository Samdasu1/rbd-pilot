"""Retry policy for Exp 2 judge entries that failed validation.

Usage:
    exp2_retry_failed.py --judges grok-4 gemini-2.5-pro       # frontier only
    exp2_retry_failed.py --judges phi-3-medium-14b-instruct   # ollama only
    exp2_retry_failed.py                                       # all failing judges
    exp2_retry_failed.py --pass 2                             # second attempt only

Semantics: for each (eid, condition, judge_model_id) whose existing judge file
has validation.passed=false, move the failed file to an attic directory and
re-invoke run_judge. After two such passes, any still-failing entry is treated
as a permanent fail (its second-attempt file remains in place with
validation.passed=false; the original is preserved in attic_1).

Concurrency: same ThreadPoolExecutor pattern as exp2_run.py. Safe to run while
exp2_run.py is also processing missing files — they touch disjoint file sets
(run_judge skips when file exists; we only act on files that already exist with
validation.passed=false, after moving them out of judge/).
"""

import argparse
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from exp2_run import (
    BASE, EXAMPLES_DIR, exec_path, judge_path, get_active_set, run_judge
)


def find_failed_files(judges_filter: set[str] | None) -> list[tuple[str, str, str, Path]]:
    """Return [(eid, condition, judge_model_id, file_path)] for failing files."""
    judge_dir = BASE / "judge"
    out = []
    for fp in sorted(judge_dir.glob("*.json")):
        try:
            d = json.loads(fp.read_text())
        except Exception:
            continue
        if d.get("validation", {}).get("passed", True):
            continue
        eid = d.get("example_id")
        cond = d.get("condition")
        jm = d.get("judge_model_id")
        if not (eid and cond and jm):
            continue
        if judges_filter and jm not in judges_filter:
            continue
        out.append((eid, cond, jm, fp))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judges", nargs="+", default=None,
                    help="Restrict retry to these judge model ids")
    ap.add_argument("--pass", dest="attempt_no", type=int, choices=[1, 2], default=1,
                    help="Which attempt this run records (used for attic dir name).")
    ap.add_argument("--workers", type=int, default=4,
                    help="Thread pool size. Keep low for ollama (model swap).")
    ap.add_argument("--limit", type=int, default=None,
                    help="Cap number of retries (useful for smoke test).")
    args = ap.parse_args()

    judges_filter = set(args.judges) if args.judges else None
    failed = find_failed_files(judges_filter)
    if args.limit:
        failed = failed[: args.limit]

    if not failed:
        print("No failed-validation files matching filter.")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    attic = BASE / "judge" / f"_retry_attempt{args.attempt_no}_{date}"
    attic.mkdir(exist_ok=True)

    print(f"=== RETRY pass {args.attempt_no}: {len(failed)} failed entries ===")
    by_model = {}
    for _, _, jm, _ in failed:
        by_model[jm] = by_model.get(jm, 0) + 1
    for jm in sorted(by_model):
        print(f"  {jm:30s} {by_model[jm]:4d}")
    print(f"Attic: {attic}")

    # Group by eid so we load example/exec only once
    by_eid: dict[str, list[tuple[str, str, str, Path]]] = {}
    for row in failed:
        by_eid.setdefault(row[0], []).append(row)

    n_now_pass = 0
    n_still_fail = 0
    n_load_skip = 0
    cost_total = 0.0

    for i, eid in enumerate(sorted(by_eid), 1):
        ex_path = EXAMPLES_DIR / f"{eid}.yaml"
        if not ex_path.exists():
            print(f"  [{i}/{len(by_eid)}] {eid} -> SKIP (example yaml missing)")
            n_load_skip += len(by_eid[eid])
            continue
        ex = yaml.safe_load(ex_path.read_text(encoding="utf-8"))
        delegation = ex["delegation"]
        artifact = ex["artifact"]["text"].rstrip()
        try:
            active_set = get_active_set(eid)
        except Exception as e:
            print(f"  [{i}/{len(by_eid)}] {eid} -> SKIP (active_set unavailable: {e})")
            n_load_skip += len(by_eid[eid])
            continue

        # Group within eid by condition (exec output is per-condition)
        by_cond: dict[str, list[tuple[str, str, str, Path]]] = {}
        for row in by_eid[eid]:
            by_cond.setdefault(row[1], []).append(row)

        print(f"  [{i}/{len(by_eid)}] {eid} active_set={active_set}  conditions={list(by_cond)}")
        for cond, rows in by_cond.items():
            exec_p = exec_path(eid, cond)
            if not exec_p.exists():
                print(f"    {eid} :: {cond} -> SKIP (no executor output)")
                n_load_skip += len(rows)
                continue
            output_text = json.loads(exec_p.read_text())["output_text"]

            # Move each failed file to attic
            jms_to_retry = []
            for _, _, jm, fp in rows:
                target = attic / fp.name
                if target.exists():
                    target.unlink()
                shutil.move(str(fp), str(target))
                jms_to_retry.append(jm)

            # Dispatch retry in parallel
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {
                    pool.submit(run_judge, eid, cond, jm, delegation, artifact,
                                output_text, active_set): jm
                    for jm in jms_to_retry
                }
                for fut in as_completed(futures):
                    jm = futures[fut]
                    try:
                        ok, c = fut.result()
                        cost_total += c
                        # Read new file to confirm validation state
                        new_fp = judge_path(eid, cond, jm)
                        passed = False
                        if new_fp.exists():
                            try:
                                nd = json.loads(new_fp.read_text())
                                passed = nd.get("validation", {}).get("passed", False)
                                # Annotate the retry attempt in the file itself
                                nd["retry_attempt"] = args.attempt_no
                                new_fp.write_text(json.dumps(nd, indent=2))
                            except Exception:
                                passed = False
                        if passed:
                            n_now_pass += 1
                        else:
                            n_still_fail += 1
                    except Exception as e:
                        print(f"    {eid} :: {cond} JUDGE[{jm}] -> THREAD-EXCEPTION: {e}")
                        n_still_fail += 1

    print()
    print(f"Retry pass {args.attempt_no} complete:")
    print(f"  now_pass    = {n_now_pass}")
    print(f"  still_fail  = {n_still_fail}")
    print(f"  load_skip   = {n_load_skip}")
    print(f"  cost_added  = ${cost_total:.4f}")
    print(f"  attic       = {attic}")


if __name__ == "__main__":
    main()
