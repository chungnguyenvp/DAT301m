# Final whole-branch review — cleanup round 2

Base: `a683096792e1eeb34d304ba83d58555120dddc4b`  
Reviewed head: `f835d33325c58fbcaa21771929d109f86391cebf` (`feat/cleanup-round2`)  
Assessment: **Ready to merge: Yes**, within the authorized cleanup scope. No mandatory fix wave. The minor items below should remain follow-ups; merging does not establish a complete source corpus or readiness for question generation/fine-tuning.

## Scope and method

Read the complete changed implementation and tests, reviewed CSV changes, final report/follow-ups, Tasks 1–8 and the cleanup design, task reports/reviews, and the deferred ledger. Independently inspected current JSONL/documents, Git baselines, OCR source markers, converted Word XML, and reproducibility snapshots. Targeted probes used `py -3.13 -B -X utf8` and in-memory objects. No source/data/index/checkout mutation, no full-suite rerun, and no pipeline rerun. Only this scratch report was written.

The existing 179-test gate is prior execution evidence, not a test run claimed by this reviewer. The two Task 8 snapshots contain 43 identical hashes. All 42 generated data files still match those hashes; `PROCESSING_REPORT.md` is the sole difference because its final manually authored report was edited after the snapshot. This is not generated-data drift.

## Strengths

- **Retention and integration:** independently counted 33 documents, 17,850 source units, 18,790 versions and 17,423 records returned at the cutoff. Comparing with pre-Task-7 commit `689a7bb`, all 18,790 records retain every old field exactly when `hl_ngoai_le` is removed. No raw files changed. There are no `#` unit IDs, and no current appendix has multiple versions that could make the one-row-per-unit annex review ambiguous.
- **Word extraction:** direct row/cell traversal eliminates nested traversal duplication. An independent vertical-merge probe returned `Merged | One`, then `Two`, retaining the merged text once. Scanning all converted Word documents found no text-bearing `w:sdt`/`w:customXml` inside tables, so the wrapper limitation below causes no current-corpus loss.
- **Structure:** joining the final TT51 and QCVN documents equals the pre-split text at `860009f` after the intended 32 TOC-line removals and whitespace normalization. No other baseline document has lines matching the TOC filter. The current QCVN has 84 consecutive articles; deep numbered items remain inside their clause, avoiding false repeated point addresses. The only removed source-unit IDs outside TT51 are TT108 `d8:k8:a/b/c`, relocated under restored `d8:k9`; added TT36/TT108 structural IDs correspond to the reviewed OCR corrections. Current closing blocks number at most one per document and contain no swallowed article headings.
- **Digit labels and quote boundaries:** targeted probes confirm `k1)` before any article stays in `mo_dau`, and a real multiline quoted block containing a standalone `BỘ TRƯỞNG` remains in the article. The reviewed amendment now adds `nd_168_2024:d41:k4:k1` without closing/replacing point `k`.
- **OCR provenance:** all three `source.sha256` markers independently match the corresponding raw PDFs. DPI is part of the page-cache path, ties retain the base OCR, retries cannot replace text with blank output, invalid retry/page/DPI inputs fail, and failed Tesseract output is not persisted as a page. Tests cover these behaviors. The final report correctly calls the syllable measure a heuristic and discloses its inability to measure semantic/numeric/table correctness.
- **Annotations and validity:** independently confirmed 184 unchanged-content flags, 107 form annexes / 51 content annexes, 21 poor-quality records, the 7 approved overrides, and 22 exception rows (8 extension, 5 delay, 9 content milestone). Hierarchical attachment uses a colon boundary, avoiding `k1`/`k10` leakage. Original validity fields remain untouched. Rechecking boundary dates confirms TT12 has 17 live extended units on 2027-02-28 and none on 2027-03-01; delayed TT108 units enter then, and the old/new conditional overlap ends on the approved boundary. The code follows the approved role/condition contract, including applying content milestones to all versions.
- **Claims match scope:** missing QCVN image annexes M/N/O/P, TT108 `pl12` table, and ND39 `pl1` body are explicitly retained as limitations. No completeness or training-readiness claim is made. The report also identifies partial-annex conditions and the need to interpret conditions on the returned records.

## Issues — Critical

None found.

## Issues — Important

None found in the current corpus or authorized Tasks 1–8. No issue requires a pre-merge code/data fix.

## Issues — Minor

1. **Report date table omits the derived document.** `data/processed/PROCESSING_REPORT.md:31` introduces the final effective-date table, but its 32 rows omit `qcvn_41_2024`; `data/processed/effective_dates.csv` correctly includes `2025-01-01`, source `van_ban_cha`. Add the QCVN row when polishing the report so the table covers the stated 33 documents. Data and the live-record count are correct.

2. **Report metrics reference is not reproducible from a fresh checkout.** `data/processed/PROCESSING_REPORT.md:3` cites `task8_metrics.py` without a path/link, while the actual script is ignored scratch material. A future documentation patch should provide a tracked metrics command/script or explicitly identify the scratch calculation and the public inputs/formulas. This affects report auditability, not the pipeline's verified output reproducibility.

3. **Future digit-point amendment references remain unsupported.** `src/lawproc/amendments.py:12` and `:17` still limit `ADDR`/`POINT` to letter-only point labels. A future instruction targeting an existing `k1` can fail to resolve the point or resolve only its containing clause. The current `k1` addition is correctly represented by the reviewed CSV and applied; no current reviewed output depends on resolving such a reference. Extend these patterns and add a reference-resolution test before processing further amendments with digit labels.

4. **Future QCVN clause additions fail in the lead-in check.** `src/lawproc/apply.py:8`, `:47`, `:183` recognize labels using only DIEU/KHOAN/DIEM, whereas `parse_units` also accepts `3.2.` for configured QCVN documents. A future `bo_sung` with `new_text="3.2. Khoản bổ sung"` is rejected as unplaceable lead-in. This fails visibly and does not affect the current reviewed amendment set. Teach the check the target-document-specific dotted pattern when that capability is needed.

5. **Closing detection is not constrained to the final article.** `src/lawproc/structure.py:19` and `:145` accept a signature-looking line after any article. In an in-memory input `Điều 1. A / Q. TRƯỞNG PHÒNG / Điều 2. B`, the second article is retained as text inside `ket_thuc` instead of an article unit. No current closing block contains such a swallowed heading. The design's stronger final-article guard remains a future-input hardening task, along with a regression test. The ledger's stray-quote concern also remains hypothetical for this corpus; the existing lookahead already resets truly unclosed quotes, and the actual multiline quote probe passes.

6. **Word wrapper handling and table structure remain limited.** `src/lawproc/extract.py:26` and `:39` skip wrapped block/row/cell content and flatten nested table rows using the same separators as outer rows. The corpus-wide XML check found no affected wrapper text, and flattening follows this task's text output contract. Preserve or explicitly reject wrappers and retain stronger table boundaries if future sources or downstream table processing require them.

7. **A few planned regression cases are only implicit.** `tests/test_structure.py:254` uses a single-line quote whose first character is already a quote, so it does not exercise a later standalone closing line inside an open multiline quote. `tests/test_extract.py:187` tests horizontal merging, not vertical merging. There is also no explicit processed assertion for one closing unit per document. Independent probes/current-corpus checks pass all these cases; adding permanent tests is useful, but no defect was observed that makes them a merge condition.

## Deferred-ledger disposition

| Ledger item | Final disposition |
|---|---|
| Task 1 wrappers / nested separators | Minor future-input limitations; corpus inspected directly, no wrapper text loss. |
| Task 1 one unexplained `FAIL parse` | No reproducible current failure; both later pipeline passes and current generated hashes support closure. Do not block without a reproducer. |
| Task 1 candidate CSV line endings | No substantive final branch candidate diff; no action required. |
| Task 2 letter-only amendment references | Retain Minor item 3; current approved `k1` output correct. |
| Task 2 negative `k1)` test | Independent negative probe passes; optional permanent regression coverage. |
| Task 3 weak quote test | Retain Minor item 7; real multiline probe passes. |
| Task 3 stray quotes / broad signature prefixes | No observed corpus damage; retain future-input hardening in Minor item 5. |
| Task 3 one-closing / no-`#` invariant | Current independent audit passes both; optional stronger permanent invariant. |
| Task 4 dotted `bo_sung` | Retain Minor item 4; explicit error, no current amendment affected. |
| Task 4/5/6 source gaps | Explicit accepted scope limitations, still required before treating the corpus as complete. |
| Task 5 intermittent Word COM diagnostic | Focused rerun previously passed; no branch change to conversion and no unresolved reproducible failure. |
| Task 8 untracked metrics reference | Retain Minor item 2; generated-data reproducibility is separately verified. |

## Assessment

**Ready to merge: Yes.** This branch completes the approved cleanup scope with no identified critical or important finding. Keep the source gaps and minor future-input limitations visible; they are not evidence that the corpus is ready for complete legal retrieval or data generation.


## Final documentation fix verification

# Final documentation-fix review

Base: `f835d33325c58fbcaa21771929d109f86391cebf` (`feat/cleanup-round2`). Reviewed only the uncommitted changes to `data/processed/PROCESSING_REPORT.md` and `docs/superpowers/followups/2026-10-09-legal-processing-followups.md` described in `final-docfix.diff`.

**Verdict: both requested minor findings are addressed; no new breakage found in this documentation diff. Ready to merge within the previously reviewed scope.**

1. **Minor 1 — omitted QCVN date row: resolved.** The report now includes `qcvn_41_2024 | 2025-01-01 | van_ban_cha`, matching `effective_dates.csv`. The documented effective-date table has 33 distinct rows, and all 33 `doc_id`, `hl_chot`, and `nguon` triples match the CSV.
2. **Minor 2 — untracked audit reference: resolved.** The report identifies `task8_metrics.py` as ignored scratch material and supplies a standalone Python 3.13 calculation using tracked processed files and `lawproc.validity.in_force_at`. Run from the repository root, the documented snippet reproduces 33 documents, 17,850 units, 18,790 versions, 17,423 live records at the cutoff, 107 form/51 content annexes, 184 unchanged versions, and 21 poor-quality versions.

The added follow-up bullets accurately retain the previous review's Minor items 3–7 as future-input limitations and permanent-test work. They do not change the earlier merge assessment or claim that the source corpus is complete.

Focused read-only validation: `py -3.13 -B -X utf8 .superpowers/sdd/2026-10-09-cleanup-round2/task8_doccheck.py` passed, including the report snippet and 33/33 date-table comparison. `git diff --check` passed. `git status --short` showed only the two intended Markdown modifications before this review file was written. I did not rerun the full test suite or pipeline and did not alter source, data, or HEAD.


Minor items 1–2 were fixed after the reviewed head; items 3–7 remain nonblocking follow-ups in `docs/superpowers/followups/2026-10-09-legal-processing-followups.md`. No parser or generated JSONL changed in this final documentation wave. The complete cleanup has not been merged to main.
