# `AmbiguousDelegation-50-R1` (pilot v1.1)

> Status: under construction. **Private** by default — not committed to public `rbd-harness`.

This directory holds the 50-example pilot dataset for the responsibility-bearing delegation paper. Construction protocol is fully specified in `paper/6. agent/docs/spec_dataset_v1.0.md`.

## Layout

```
data/pilot_v1.1/
├── README.md                       (this file)
├── INDEX.jsonl                     one line per example; updated as examples are added
├── examples/                       50 YAML records, ad_r1_001.yaml … ad_r1_050.yaml
├── annotations/                    raw per-annotator JSON (author, LLM_1, LLM_2, optional humans)
├── provenance/modified-real/       private source records for the 20 modified-real examples
└── stats/                          alpha_per_dim.json, coverage_matrix.json, human_llm_spearman.json
```

## Privacy

- This directory is **never** committed to `rbd-harness` (the public repo).
- Modified-real artifacts are anonymized at construction time; raw source records live under `provenance/modified-real/` and are not exported.
- Public dataset card (when published) will exclude `provenance/`, `annotations/`, and any field marked `source_provenance`.

## Build phase status

Per `spec_dataset_v1.0.md` §9 build order:

- [in progress] step 2: synthetic 30 examples (batch 1 = 5 example proof-of-format)
- [todo] step 3: modified-real 20 examples
- [todo] step 4: author r* on all 50
- [todo] step 5: LLM annotators on all 50
- [todo] step 6: α computation
- [todo] step 7: dim definition revision if needed
- [todo] step 8: 20-example human subset annotation
- [todo] step 9: human–LLM stats
- [todo] step 10: acceptance gates (G-D-01..10)

Once acceptance gates pass, this dataset is frozen at v1.0 and used for `spec_pi_v1.0` projection runs.

## Per-example schema

See `spec_dataset_v1.0.md` §7 for the canonical schema.

## Convention — `word_count` is canonical via `wc -w`

The `word_count` field in each example YAML is the output of `wc -w` on the raw artifact text (the YAML block under `text: |`, excluding the YAML scaffolding). Eyeball estimates have been observed to drift 15–25 words above `wc -w` and led to G-D-05 acceptance-gate failures during pilot batch 1. New examples must run `wc -w` and record that exact integer.

Quick check across all examples:

```bash
cd data/pilot_v1.1/examples
for f in ad_r1_*.yaml; do
  declared=$(grep "word_count:" "$f" | head -1 | grep -o "[0-9]*")
  actual=$(awk '/^  text: \|/,/^  source_provenance:/' "$f" \
           | grep -v "^  source_provenance:" \
           | grep -v "^  text: |" \
           | wc -w)
  echo "$f  declared=$declared  actual=$actual"
done
```

## Build references (frozen at spec time)

- Delegation pool: `spec_dataset_v1.0.md` §3 (T01–T10)
- Engineered-flaw catalog: `spec_dataset_v1.0.md` §5 (21 flaw codes across 7 R1 dims)
- Coverage matrix: `spec_dataset_v1.0.md` §2 (35 single + 10 dual + 5 ambiguous)
- Hidden-intent anchors: `formalization_v1.1.md` §5 (0.0 / 0.3 / 0.7 / 1.0)
