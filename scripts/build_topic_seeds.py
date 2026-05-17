"""Extract topic seeds from references.bib (+ optional PDF abstracts).

Output: data/main_v1.0/topic_seeds.jsonl — one record per bibtex entry:
  {key, title, primary_class, year, abstract (optional), source_pdf (optional)}

Used by gen_examples_main.py --seed-from-references to inject random topic
anchors into the synthetic-artifact generation prompt. Only title + class
are load-bearing for the seed; abstract is enrichment.

Run from repo root:
  python3 scripts/build_topic_seeds.py
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB = ROOT / "paper" / "references.bib"
OUT = ROOT / "data" / "main_v1.0" / "topic_seeds.jsonl"
PDF_DIRS = [ROOT / "reference", ROOT / "reference2", ROOT / "reference3"]

ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\s*\}\s*\n", re.DOTALL)
FIELD_RE = re.compile(r"^\s*(\w+)\s*=\s*[\{\"](.*?)[\}\"]\s*,?\s*$", re.MULTILINE | re.DOTALL)


def parse_bib(text: str) -> list[dict]:
    """Tolerant bibtex parser — extracts top-level fields per entry."""
    entries: list[dict] = []
    # split by @type{key, ... } blocks
    depth = 0
    buf: list[str] = []
    in_entry = False
    key_capture = []
    capturing_key = False
    cur_type = None

    i = 0
    while i < len(text):
        c = text[i]
        if not in_entry and c == "@":
            # start of entry
            j = text.find("{", i)
            if j == -1:
                break
            cur_type = text[i + 1:j].strip().lower()
            in_entry = True
            depth = 1
            i = j + 1
            buf = []
            capturing_key = True
            key_capture = []
            continue
        if in_entry:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    body = "".join(buf)
                    rec = {"_type": cur_type, "_key": "".join(key_capture).strip()}
                    for fm in FIELD_RE.finditer(body):
                        rec[fm.group(1).lower()] = re.sub(r"\s+", " ", fm.group(2).strip())
                    entries.append(rec)
                    in_entry = False
                    i += 1
                    continue
            if capturing_key:
                if c == "," and depth == 1:
                    capturing_key = False
                else:
                    key_capture.append(c)
            else:
                buf.append(c)
        i += 1
    return entries


_NORM_RE = re.compile(r"[^a-z0-9]+")


def _norm(s: str) -> str:
    return _NORM_RE.sub("", s.lower())


def find_pdf(key: str, eprint: str | None, title: str | None = None) -> Path | None:
    title_words: list[str] = []
    if title:
        # strip BibTeX braces, take first 5 'content' words length>=4
        clean = re.sub(r"[{}]", "", title).lower()
        title_words = [w for w in re.findall(r"[a-z0-9]+", clean) if len(w) >= 4][:5]
    for d in PDF_DIRS:
        if not d.exists():
            continue
        for pdf in d.glob("*.pdf"):
            stem = pdf.stem.lower()
            if eprint and eprint.lower() in stem:
                return pdf
            if key.lower() in stem:
                return pdf
            if title_words:
                # require >= 3 of the first-5 content words to appear in stem
                stem_norm = _norm(stem)
                hits = sum(1 for w in title_words if _norm(w) in stem_norm)
                if hits >= min(3, len(title_words)):
                    return pdf
    return None


def extract_abstract(pdf: Path, *, max_chars: int = 1500) -> str | None:
    """Pull text of page 1 with pdftotext; heuristically grab the abstract."""
    try:
        proc = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "1", "-layout", str(pdf), "-"],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    text = proc.stdout or ""
    # heuristic: find "Abstract" then grab the next 1-3 paragraphs (cutoff at "1." / "Introduction")
    m = re.search(r"\bAbstract\b[\s\.\—\-:]*", text, re.IGNORECASE)
    if not m:
        return None
    after = text[m.end():]
    cut = re.search(r"\n\s*(1\.?\s*Introduction|I\.?\s+Introduction|Introduction\b)", after, re.IGNORECASE)
    if cut:
        after = after[: cut.start()]
    abs_text = re.sub(r"\s+", " ", after).strip()
    return abs_text[:max_chars] if abs_text else None


def main() -> int:
    if not BIB.exists():
        print(f"missing: {BIB}", flush=True)
        return 1
    text = BIB.read_text(encoding="utf-8")
    entries = parse_bib(text)
    print(f"parsed {len(entries)} bibtex entries", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    n_with_abs = 0
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in entries:
            key = rec.get("_key", "?")
            title = rec.get("title", "").strip()
            if not title:
                continue
            seed = {
                "key": key,
                "title": title,
                "primary_class": rec.get("primaryclass", "").strip() or rec.get("journal", "").strip() or "",
                "year": rec.get("year", "").strip(),
            }
            pdf = find_pdf(key, rec.get("eprint"), title=title)
            if pdf is not None:
                seed["source_pdf"] = pdf.name
                abs_text = extract_abstract(pdf)
                if abs_text:
                    seed["abstract"] = abs_text
                    n_with_abs += 1
            fh.write(json.dumps(seed, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({n_with_abs} with abstract / {len(entries)} total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
