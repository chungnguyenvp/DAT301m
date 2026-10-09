# EDA corpus — final review and verification

Branch: `codex/eda-corpus`; base main `bb5e46d`. Four tasks implemented; evaluation allocation is a pending 150-slot proposal. No raw/processed edits or QA/training generation.

Verification: 201 tests passed; full fresh-kernel notebook executions gave identical numerical metrics and initial matrix. The final prose-only correction preserves all 25 executed code cells and outputs. Ten figures visually checked. All 137 raw/processed file hashes unchanged.

## Whole-branch review

# Final whole-branch review

Reviewed base `bb5e46d` through head `23dbd8d3d5752c2c3dd2fe7b8c8f26f03e0548cf` using the single full-source `final-branch.diff`, implementation plan/design, Task 3 controller adaptations, and existing task review evidence. Review is read-only except this scratch report. No test suite or notebook execution was repeated.

Verdict: one minor documentation finding; no critical or important implementation findings.

## Minor

- **[P3] Correct the notebook's introductory analysis-population statement — `notebooks/01_eda_kho_luat.py:21` (and the corresponding first markdown cell of `notebooks/01_eda_kho_luat.ipynb`).** The introduction currently says “E1–E10 dùng một bản đại diện mới nhất cho mỗi `unit_id` có hiệu lực tại T.” That is false for E5's reviewed amendment rows and all stored versions, E6's historical/future timeline, and E10's source-gap audit. A reader relying on the notebook alone can therefore interpret the historical counts as active-at-T counts. `reports/eda/findings.md:5` already makes the correct distinction after the Task 4 fix. Apply the same population distinction to the notebook introduction. This changes explanatory markdown only; it does not require recalculating the unchanged statistics.

## Integration assessment

- Computational architecture is appropriately bounded: helpers hold reusable extraction, tokenization, similarity, and deterministic allocation; the notebook orchestrates read-only input analysis; only tokenizer paths extend existing production configuration. No QA generation, training, or production retrieval behavior was introduced.
- Active record versus distinct-unit denominators are deliberate and consistently reported in numeric outputs. Six conditional versions remain visible; latest representatives are explicitly descriptive, and chunk candidates are not claimed as universally valid legal provisions.
- E2's legal support scope is a proposal subject to confirmation, not a completeness claim. E3 distinguishes body-only and headed measurements and reserves unmeasured metadata/condition/prompt overhead. E4 first-frame/first-point regex counts and structural points are qualified. E5 counts approved rows and changed historical versions; E6 preserves the TT12 exclusive extension endpoint. E7 group TF-IDF, E8 textual similarity, E9 limited reference parsing, and E10 quality heuristics/source gaps are not overstated as validated legal equivalence or OCR accuracy.
- The report's numbers and matrix pivot agree with the checked source-generated summary and CSV. The matrix is a deterministic 150-slot proposal, preserves existing manual edits on rerun, and clearly remains pending human approval. No generated questions or train/eval leakage was introduced.
- Tokenizer source URLs, exact byte counts, and SHA256 assertions are tracked; analysis is self-contained without scratch-path dependencies. Existing pinned requirements remain Windows-oriented (`pywin32`); this is a documented platform limitation rather than a new promise of a fully portable installation. The explicitly named kernel and registration command address the known local Anaconda/Python313 ambiguity.
- Prior evidence accepted without redundant reruns: 201 passing tests; repeated fresh-kernel execution with stable metrics and matrix; source/notebook audit; ten visually reviewed figures; 137 unchanged raw/processed hashes. Current head matches the requested review head and the working tree was clean when inspected.

After the minor introduction correction, this branch is suitable for the human matrix-approval and integration-choice steps. This review does not approve the legal scope/allocation on behalf of the user and does not authorize merging.


## Scoped final verification

# Final scoped rereview

**PASS.** The sole P3 finding from `final-branch-review.md` is resolved.

Reviewed the working-tree diff against `23dbd8d`, the corrected source introduction and first notebook markdown cell, and `final-fix-report.md`. The introductory population statement now correctly limits newest-active representatives to active-at-T unit statistics, separately identifies E5 approved amendment rows and stored version history, E6 all-record historical/future analysis, and E10 all-version source-gap auditing. It retains the descriptive-statistics and conditional-version caveats.

Focused independent structural comparison against `23dbd8d` confirmed that only the source of notebook markdown cell 0 changed. All 25 code cells remain exactly equal as parsed JSON, including code, execution counts, outputs and cell metadata; all cell IDs and top-level notebook metadata are unchanged. The source diff is only the corresponding four-line explanatory correction.

No residual findings. No test suite or notebook computation was rerun; only this scratch review was written. The final whole-branch review is now PASS, with human matrix approval and integration choice still pending and no merge authorization implied.
