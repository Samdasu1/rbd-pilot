#!/usr/bin/env python3
"""Generate Stage 1 human-eval packages — pilot v1.3.

Reads:
  - data/pilot_v1.1/_stage1_sampling.json  (pre-registration: which examples per dim batch)
  - data/pilot_v1.1/examples/{eid}.yaml     (artifact + delegation)
  - data/pilot_v1.1/execution/{eid}__{cond}__opus.json (agent output)

Per-batch structure (per experiment_design_v1.3 §2.6):
  - 9 examples × 2 conditions (direct_naive + projection_driven) = 18 packages per batch
  - 3 batches: R1.7, R1.4, R1.1

Anonymization (sanitization per human_annotation/README.md §3):
  - example_id ad_r1_NNN  →  pkg_NN within batch
  - condition direct_naive/projection_driven → variant_A/variant_B (random per-package)
  - dim code R1.X → descriptive name
  - Strip self-claim JSON line (first line if `{"covered_dims": ...}`) — agent self-report
    must not leak into human evaluation
  - Random shuffle (seed=42) so paired (eid, cond) packages are not adjacent

Output:
  - human_annotation/texts/stage1/{R1.7|R1.4|R1.1}/pkg_NN.md  (54 files)
  - human_annotation/texts/stage1/_mapping.csv  (PRIVATE, decode key)

Usage:
    python gen_stage1_packages.py
"""

import csv
import json
import random
import re
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/treu46/paper/6. agent")
SAMPLING_PATH = ROOT / "data/pilot_v1.1/_stage1_sampling.json"
EXAMPLES = ROOT / "data/pilot_v1.1/examples"
EXECUTION = ROOT / "data/pilot_v1.1/execution"
OUT_ROOT = ROOT / "human_annotation/texts/stage1"

DIM_DESCRIPTIVE = {
    "R1.1": "Conceptual reconstruction",
    "R1.4": "Novelty assessment",
    "R1.7": "Citation and scholarship",
}

DIM_ANCHORS = {
    "R1.1": """s=1  Restates surface phrasing without changing the conceptual object.
     Adds no framing improvement.

s=3  Identifies one conceptual issue and proposes a tighter framing,
     partially supported.

s=5  Names the load-bearing concept, shows where the draft drifts from
     it, and proposes a reframing that survives prior-work contrast.""",
    "R1.4": """s=1  Asserts novelty without specific contrast.

s=3  Names one prior work and articulates the delta.

s=5  Maps against the nearest 3-5 works; identifies sharp vs rhetorical
     delta. Proposes positioning text.""",
    "R1.7": """s=1  No citation-level engagement.

s=3  Flags one missing or wrong citation.

s=5  Audits every load-bearing citation against the source. Flags missing
     key works in the relevant cluster. Suggests insertions with
     bibliographic precision.""",
}

TEMPLATE = """# Annotation Package — {pkg_id}

```
package_id: {pkg_id}
active set you need to score: [{dim_name}]
```

> 이 패키지에는 sanitization을 위해 hidden intent vector, engineered flaws, agent identity, 다른 LLM judge 점수, agent의 self-claim이 모두 제거되어 있습니다.

---

## A. Delegation (사용자가 agent에게 보낸 요청)

```
{delegation}
```

---

## B. Artifact (저자가 작성한 원본 — 평가 대상이 review한 텍스트)

```
{artifact}
```

---

## C. Agent output (평가 대상)

```
{agent_output}
```

---

## D. Anchor (채점 기준 — 영문 그대로, source of truth)

### {dim_name}

```
{anchor}
```

---

## E. 답변 row (이대로 표에 채워 주세요)

```
package_id : {pkg_id}
dim        : {dim_name}
score      : ___      (1 ~ 5 정수)
rationale  : ___      (12–600자, output에서 인용/paraphrase 1개 이상 필수)
confidence : ___      (0.0 ~ 1.0)
blockers   : ___      (보통 빈 칸)
```
"""

_SELF_CLAIM_RE = re.compile(r'^\s*\{\s*"covered_dims"\s*:.*?\}\s*$', re.MULTILINE)


def strip_self_claim(output_text: str) -> str:
    """Remove the first-line `{"covered_dims": ...}` JSON if present.

    Per experiment_design_v1.3 §2.4 — sanitization removes the JSON line text;
    body priming effect on the rest of the output is captured by the
    direct_naive vs direct_with_claim ablation, not by this stripping.
    """
    if not output_text:
        return ""
    first_line, _, rest = output_text.lstrip().partition("\n")
    if first_line.strip().startswith('{"covered_dims"') and first_line.strip().endswith("}"):
        return rest.lstrip()
    return output_text


def main() -> None:
    sampling = json.loads(SAMPLING_PATH.read_text())
    seed = sampling["rng_seed"]
    rng = random.Random(seed)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    mapping_rows = []
    cache_examples = {}

    for dim, batch in sampling["batches"].items():
        eids = batch["selected_ids"]
        conditions = sampling["conditions_evaluated_per_example"]
        pairs = [(eid, cond) for eid in eids for cond in conditions]
        rng_b = random.Random(seed + hash(dim) % 1000)
        rng_b.shuffle(pairs)

        out_dir = OUT_ROOT / dim
        # clear stale
        if out_dir.exists():
            for f in out_dir.glob("pkg_*.md"):
                f.unlink()
        out_dir.mkdir(parents=True, exist_ok=True)

        for idx, (eid, cond) in enumerate(pairs, 1):
            pkg_id = f"{dim.replace('.', '_')}_pkg_{idx:02d}"
            if eid not in cache_examples:
                cache_examples[eid] = yaml.safe_load((EXAMPLES / f"{eid}.yaml").open())
            ex = cache_examples[eid]
            delegation = ex["delegation"].strip()
            artifact = ex["artifact"]["text"].rstrip()

            exec_p = EXECUTION / f"{eid}__{cond}__opus.json"
            if not exec_p.exists():
                print(f"  WARN missing executor output for {eid}/{cond}: {exec_p}", file=sys.stderr)
                continue
            exec_blob = json.loads(exec_p.read_text())
            agent_output = strip_self_claim(exec_blob["output_text"]).rstrip()

            content = TEMPLATE.format(
                pkg_id=pkg_id,
                dim_name=DIM_DESCRIPTIVE[dim],
                delegation=delegation,
                artifact=artifact,
                agent_output=agent_output,
                anchor=DIM_ANCHORS[dim],
            )
            (out_dir / f"{pkg_id}.md").write_text(content)

            mapping_rows.append({
                "batch": dim,
                "package_id": pkg_id,
                "example_id": eid,
                "condition": cond,
                "dim": dim,
                "executor_model": exec_blob.get("executor_model"),
                "prompt_version": exec_blob.get("prompt_version"),
            })
            print(f"  wrote {dim}/{pkg_id}.md  ←  {eid} / {cond}")

    mapping_path = OUT_ROOT / "_mapping.csv"
    with mapping_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=mapping_rows[0].keys())
        writer.writeheader()
        writer.writerows(mapping_rows)
    print(f"\nwrote {mapping_path.relative_to(ROOT)} (PRIVATE — do not upload to gist)")
    print(f"\nTotal: {len(mapping_rows)} packages across {len(sampling['batches'])} batches.")
    print(f"Per batch: {len(sampling['batches']['R1.7']['selected_ids']) * 2} packages "
          f"= {len(sampling['batches']['R1.7']['selected_ids'])} examples × "
          f"{len(sampling['conditions_evaluated_per_example'])} conditions.")


if __name__ == "__main__":
    main()
