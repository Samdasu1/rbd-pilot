#!/usr/bin/env python3
"""Rank 50 examples by R1.7-relevance: citation density + section type heuristics."""
import json, re, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX_DIR = ROOT / "data/pilot_v1.1/examples"

# Citation patterns
PATTERNS = [
    re.compile(r"\b[A-Z][a-zA-Z]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z]+)?\s+et\s+al\.?,?\s*\(?\d{4}\)?", re.U),  # "Smith et al., 2020"
    re.compile(r"\b[A-Z][a-zA-Z]+\s+(?:and|&)\s+[A-Z][a-zA-Z]+,?\s*\(?\d{4}\)?", re.U),                    # "Smith and Jones 2020"
    re.compile(r"\b[A-Z][a-zA-Z]+\s+\(\d{4}\)", re.U),                                                       # "Smith (2020)"
    re.compile(r"\[\d+(?:,\s*\d+)*\]"),                                                                       # "[12]" or "[12, 13]"
]

# Section-type heuristics (citation engagement most natural in these)
INTRO_HINTS = re.compile(r"\b(introduc|related work|background|prior work|literature|we build on|building on|in contrast to|unlike)\b", re.I)
METHOD_HINTS = re.compile(r"\b(equation|update|loss function|gradient|stage|step|algorithm \d|line \d)\b", re.I)
RESULT_HINTS = re.compile(r"\b(table \d|figure \d|fig\. \d|MSE|accuracy|baseline|recall@|benchmark)\b", re.I)


def cite_count(text: str) -> dict:
    """Return per-pattern + total citation event count."""
    counts = {f"p{i}": len(p.findall(text)) for i, p in enumerate(PATTERNS)}
    counts["total"] = sum(counts.values())
    return counts


def section_class(text: str) -> str:
    intro = len(INTRO_HINTS.findall(text))
    method = len(METHOD_HINTS.findall(text))
    result = len(RESULT_HINTS.findall(text))
    if intro >= 2 and intro >= method and intro >= result: return "INTRO/RW"
    if result >= 2 and result > intro: return "RESULT"
    if method >= 2 and method > intro: return "METHOD"
    if intro >= 1: return "intro?"
    return "MIXED"


rows = []
for yf in sorted(EX_DIR.glob("*.yaml")):
    d = yaml.safe_load(yf.read_text())
    artifact = d.get("artifact", {}).get("text", "")
    cc = cite_count(artifact)
    rows.append({
        "id": d["delegation_id"],
        "wc": d.get("artifact",{}).get("word_count", 0),
        "load_bearing": ",".join(d.get("load_bearing", [])) if isinstance(d.get("load_bearing"), list) else d.get("load_bearing","")[:30],
        "R17_w": d.get("hidden_intent",{}).get("weights",{}).get("R1.7", 0),
        "R14_w": d.get("hidden_intent",{}).get("weights",{}).get("R1.4", 0),
        "cite_total": cc["total"],
        "cite_etal": cc["p0"],
        "cite_andX": cc["p1"],
        "cite_paren": cc["p2"],
        "cite_brkt": cc["p3"],
        "section": section_class(artifact),
        "preview": artifact[:140].replace("\n"," "),
    })

rows.sort(key=lambda r: (r["cite_total"], r["R17_w"], r["wc"]), reverse=True)

print(f"{'rank':>4} {'id':<11} {'cite':>4} {'R17':>4} {'R14':>4} {'wc':>4} {'sec':<9} load_bearing")
print("-"*120)
for i, r in enumerate(rows[:30], 1):
    print(f"{i:>4} {r['id']:<11} {r['cite_total']:>4} {r['R17_w']:>4.2f} {r['R14_w']:>4.2f} {r['wc']:>4} {r['section']:<9} {r['load_bearing']}")

print("\n=== preview of top 18 (citation-rich + R1.7-loaded) ===\n")
for i, r in enumerate(rows[:18], 1):
    print(f"[{i}] {r['id']}  cite={r['cite_total']} (etal={r['cite_etal']}, andX={r['cite_andX']}, paren={r['cite_paren']}, brkt={r['cite_brkt']}) R17_w={r['R17_w']} R14_w={r['R14_w']} sec={r['section']} wc={r['wc']}")
    print(f"    load_bearing: {r['load_bearing']}")
    print(f"    preview: {r['preview']}")
    print()

# Save full rank as json
out = ROOT / "data/pilot_v1.1/_r17_density_rank.json"
out.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
print(f"\nfull rank saved to {out.relative_to(ROOT)}")
