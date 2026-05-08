#!/usr/bin/env python3
"""R1.7 v2 — sharpened anchor + 6 citation-rich packages + author/peer co-annotation Form.

Pivot rationale (Stage 1 finding 2026-05-07):
  Original 18-package design failed: 50-example pool yielded only 6 examples
  with citation events ≥1 in the artifact, so R1.7 anchor had no data to act
  on. Author's own test annotations regressed to a generic intent-fit lens
  (R1.6/R1.3/R1.1 mixture) instead of R1.7 (Citation and scholarship).

v2 redesign:
  - 6 examples (009, 024, 046, 026, 016, 013) selected by citation density rank
  - 1 condition (projection_driven) — agent has J*(d) projected, R1.7 lens
    most likely to fire here
  - Anchor sharpened to citation-event count decision tree (no 'overall
    quality' pollution path)
  - No Prolific. Author + peer1 + peer2 only via single co-annotation form.

Output:
  - human_annotation/texts/stage1/R1_7_v2/R1_7_v2_pkg_NN.md  (6 files)
  - human_annotation/texts/stage1/_r17_v2_mapping.csv
  - human_annotation/recruitment/r17_v2_coannotation_form_url.txt
"""

import csv
import json
import os
import random
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv
load_dotenv(Path.home() / "research-harness" / ".env")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data/pilot_v1.1/examples"
EXECUTION = ROOT / "data/pilot_v1.1/execution"
OUT_DIR = ROOT / "human_annotation/texts/stage1/R1_7_v2"
MAPPING_PATH = ROOT / "human_annotation/texts/stage1/_r17_v2_mapping.csv"
FORM_URL_PATH = ROOT / "human_annotation/recruitment/r17_v2_coannotation_form_url.txt"

EIDS = ["ad_r1_009", "ad_r1_024", "ad_r1_046", "ad_r1_026", "ad_r1_016", "ad_r1_013"]
CONDITION = "projection_driven"
DIM = "R1.7"
DIM_NAME = "Citation and scholarship"

ANCHOR_SHARP = """Score by counting CITATION ENGAGEMENT EVENTS in the agent output.

A "citation event" = the agent does ONE of:
  (a) flags a specific citation as missing, wrong, mis-attributed, or mis-classified
      (e.g. "ScaNN is described as graph-based but is a quantization method")
  (b) names a specific work the artifact omits and explains why it matters
      (e.g. "HNSW (Malkov & Yashunin, 2018) is conspicuously absent from a
      graph-ANN intro")
  (c) audits a specific citation's venue/year/authorship against the source
      (e.g. "DiskANN venue/year — please verify")
  (d) suggests a specific insertion with bibliographic precision
      (author + year + venue, or DOI-level detail)

NOT events:
  - "Please double-check your references" / "a citation sweep is recommended"
    without naming a specific citation
  - Praise of the existing citations
  - Comments on writing, methods, claims, or evidence that do not touch the
    citation layer

Score:
  s=1  Zero events. Output does not engage the citation layer.
  s=2  One borderline event (soft / partial / non-specific).
  s=3  Exactly one clear event (a, b, c, or d).
  s=4  Two or three clear events.
  s=5  Four or more events; reads as a citation audit covering the artifact's
       load-bearing citations.

Important: this score reflects CITATION engagement only. Quality of writing,
conceptual depth, or claim-evidence alignment in OTHER parts of the output do
NOT raise this score. If the output is excellent on every other axis but
ignores the citation layer, the correct score is s=1."""

TEMPLATE = """# Annotation Package — {pkg_id}

```
package_id: {pkg_id}
active set you need to score: [{dim_name}]
```

> Sanitization: hidden intent vector, engineered flaws, agent identity, other LLM judge scores, agent self-claim line all removed.

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

## D. Anchor — sharpened (채점 기준, source of truth)

### {dim_name}

```
{anchor}
```

---

## E. 답변 row

```
package_id : {pkg_id}
dim        : {dim_name}
score      : ___      (1.0 ~ 5.0, 0.5 step)
rationale  : ___      (12-600자, 출력에서 인용/paraphrase 1개 이상)
confidence : ___      (0.0 ~ 1.0)
event_count: ___      (위 a/b/c/d 기준 카운트한 숫자)
```
"""

_SELF_CLAIM_RE = re.compile(r'^\s*\{\s*"covered_dims"\s*:.*?\}\s*$', re.MULTILINE)


def strip_self_claim(text: str) -> str:
    if not text:
        return ""
    first, _, rest = text.lstrip().partition("\n")
    if first.strip().startswith('{"covered_dims"') and first.strip().endswith("}"):
        return rest.lstrip()
    return text


def get_creds() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"].strip(),
        client_id=os.environ["google_id"].strip(),
        client_secret=os.environ["google_secret"].strip(),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/forms.body",
                "https://www.googleapis.com/auth/drive.file"],
    )


SCORE_OPTS = [f"{v:.1f}" for v in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]]
CONF_OPTS = [f"{v:.1f}" for v in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
EVENT_OPTS = [str(i) for i in range(0, 11)]


def build_packages():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for f in OUT_DIR.glob("*.md"):
        f.unlink()

    rng = random.Random(42)
    eids_shuffled = EIDS[:]
    rng.shuffle(eids_shuffled)

    rows = []
    packages = []
    for idx, eid in enumerate(eids_shuffled, 1):
        pkg_id = f"R1_7_v2_pkg_{idx:02d}"
        ex = yaml.safe_load((EXAMPLES / f"{eid}.yaml").read_text())
        delegation = ex["delegation"].strip()
        artifact = ex["artifact"]["text"].rstrip()

        exec_p = EXECUTION / f"{eid}__{CONDITION}__opus.json"
        blob = json.loads(exec_p.read_text())
        agent_output = strip_self_claim(blob["output_text"]).rstrip()

        body = TEMPLATE.format(
            pkg_id=pkg_id, dim_name=DIM_NAME,
            delegation=delegation, artifact=artifact,
            agent_output=agent_output, anchor=ANCHOR_SHARP,
        )
        (OUT_DIR / f"{pkg_id}.md").write_text(body)
        rows.append({
            "package_id": pkg_id, "example_id": eid, "condition": CONDITION,
            "executor_model": blob.get("executor_model"),
            "prompt_version": blob.get("prompt_version"),
        })
        packages.append({
            "pkg_id": pkg_id,
            "delegation": delegation, "artifact": artifact,
            "agent_output": agent_output,
        })
        print(f"  wrote {pkg_id}.md  <-  {eid} / {CONDITION}")

    with MAPPING_PATH.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"\nmapping -> {MAPPING_PATH.relative_to(ROOT)}")
    return packages


INTRO = f"""R1.7 v2 — Author + peer co-annotation (sharpened anchor + citation-rich packages).

Stage 1 pivot context: the original 18-package R1.7 design was abandoned after the author's own test pass revealed that the 50-example pool only contained 6 examples with citation events >=1 in the artifact, so R1.7 anchor had no data to act on. v2 fixes this by (i) selecting only citation-rich examples and (ii) sharpening the anchor to a citation-event-count decision tree.

You will see 6 packages (1 condition: projection_driven). Each rating: score (1.0-5.0, 0.5 step), rationale (must reference agent output), confidence (0.0-1.0), and event_count (your tally of (a)/(b)/(c)/(d) events).

Total time: ~30-45 minutes.

DIMENSION: {DIM_NAME}  -- sharpened anchor:

{ANCHOR_SHARP}

For peers: please do NOT consult the author or other peer until all 6 are submitted.

Click Next to begin."""


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n\n[... truncated, see source package ...]"


def fmt_body(p: dict) -> str:
    return (f"package_id: {p['pkg_id']}\n\n"
            f"--- DELEGATION ---\n{p['delegation']}\n\n"
            f"--- ARTIFACT (the paper section the agent reviewed) ---\n{p['artifact']}\n\n"
            f"--- AGENT OUTPUT (what you score) ---\n{p['agent_output']}\n\n"
            f"--- SHARPENED ANCHOR ({DIM_NAME}) ---\n{ANCHOR_SHARP}")


def build_form(packages):
    forms = build("forms", "v1", credentials=get_creds())
    title = "R1.7 v2 — Author + Peer Co-annotation (sharpened anchor)"
    f = forms.forms().create(body={"info": {"title": title}}).execute()
    fid = f["formId"]
    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "updateFormInfo": {"info": {"title": title, "description": INTRO},
                           "updateMask": "title,description"}}]}).execute()
    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "createItem": {"item": {"title": "Your role (select one)",
            "questionItem": {"question": {"required": True,
                "choiceQuestion": {"type": "DROP_DOWN",
                    "options": [{"value": v} for v in ["author", "peer1", "peer2"]]}}}},
            "location": {"index": 0}}}]}).execute()

    cur = 1
    for i, p in enumerate(packages, 1):
        sb = {"createItem": {"item": {
                "title": f"Rating {i} of {len(packages)} - {p['pkg_id']}",
                "description": truncate(fmt_body(p), 4000),
                "pageBreakItem": {}},
            "location": {"index": cur}}}
        score = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Score (1.0-5.0, 0.5 step)",
                "questionItem": {"question": {"required": True,
                    "choiceQuestion": {"type": "DROP_DOWN",
                        "options": [{"value": v} for v in SCORE_OPTS]}}}},
            "location": {"index": cur+1}}}
        rationale = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Rationale (quote/paraphrase, 12-600 chars)",
                "questionItem": {"question": {"required": True,
                    "textQuestion": {"paragraph": True}}}},
            "location": {"index": cur+2}}}
        conf = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Confidence (0.0-1.0)",
                "questionItem": {"question": {"required": True,
                    "choiceQuestion": {"type": "DROP_DOWN",
                        "options": [{"value": v} for v in CONF_OPTS]}}}},
            "location": {"index": cur+3}}}
        events = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Event count (your tally of a/b/c/d events; 0-10)",
                "questionItem": {"question": {"required": True,
                    "choiceQuestion": {"type": "DROP_DOWN",
                        "options": [{"value": v} for v in EVENT_OPTS]}}}},
            "location": {"index": cur+4}}}
        forms.forms().batchUpdate(formId=fid, body={"requests": [
            sb, score, rationale, conf, events]}).execute()
        cur += 5
        print(f"  added page {i}/{len(packages)}")

    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "createItem": {"item": {"title": "Completion",
            "description": "Thank you. Submit and close.",
            "pageBreakItem": {}},
            "location": {"index": cur}}}]}).execute()

    final = forms.forms().get(formId=fid).execute()
    out = {
        "form_id": fid,
        "responder_url": final.get("responderUri"),
        "edit_url": f"https://docs.google.com/forms/d/{fid}/edit",
        "n_packages": len(packages),
        "version": "R1.7_v2",
    }
    FORM_URL_PATH.write_text(json.dumps(out, indent=2))
    print(f"\nform meta -> {FORM_URL_PATH.relative_to(ROOT)}")
    print(f"\n=== R1.7 v2 co-annotation form ===")
    print(f"  responder URL: {out['responder_url']}")
    print(f"  edit URL: {out['edit_url']}")


if __name__ == "__main__":
    pkgs = build_packages()
    build_form(pkgs)
