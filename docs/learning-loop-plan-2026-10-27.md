# Evidence-driven learning loop — 2026-10-27

The aim is unattended, measurable research and engineering improvement in paper
mode. It is not model-weight training or a promise of daily profitability.

## To-do and acceptance

- [x] Add bounded prospective fill attribution: executable-price net P/L,
  midpoint gross P/L and matched entry/exit cost reconciliation. Keep legacy
  open positions unmatched rather than inventing their historical quotes.
- [x] Track spread versus combined slippage/commission, closed-fill sample
  size, win rate and best-two concentration. Diagnose hypotheses rather than
  claiming causal explanation or statistical significance.
- [x] Schedule experiment reviews every seven days of observed learning data,
  with 30 closed fills as a descriptive sample threshold. Record dated,
  evidence-linked continue/retire decisions; retirement still uses existing gates.
- [x] Supply targeted source questions for cost or signal/exit weaknesses.
  Existing source retrieval/preregistration rules require provenance and
  historical availability checks; no broad scraping or new data privileges.
- [x] Add a dependency-free paired training runner: one frozen change,
  identical source rows/cost model, chronological-third results and hashes.
  It never consumes protected holdout, grants promotion or simulates account risk.
- [x] Tag server calls and recorded findings with operator/autonomous provenance;
  retain bounded cycle outcomes across advisor reconstruction. A finding from
  operator-generated evidence cannot prove unattended research discovery.
- [x] Separate software, research completion and trading qualification scorecards
  in `/api/lab` and the read-only Research/Statistics dashboard.
- [x] Run focused regressions and prove they fail on the previous release.
- [x] Run the full suite, dashboard browser checks and `git diff --check`.
- [x] Verify a real tc02 paired comparison, without replaying any unknown job.
- [x] Update Graphify, commit/push, deploy and verify runtime controls.
- [ ] Observe a genuinely unattended production finding or repair after release.
  This is an outcome to measure, not a checkbox deployment can truthfully guarantee.

## Paired comparison

Prepare a training-only `comparison.json`, hash and upload it with the supplied
runner and `train.csv`. Preregister the question and one change before the call:

```json
{
  "baseline": {"lookback": 3, "hold": 12, "mode": "momentum"},
  "challenger": {"lookback": 3, "hold": 12, "mode": "reversal"},
  "reason": "Example of a frozen single-change diagnostic, not a strategy recommendation"
}
```

Run `python3 research_runner.py train.csv --compare comparison.json` through the
existing planned `tc02_run` capability. This example is not an instruction to
retest rejected families without new evidence. Both rules use identical costs
and fixed one-ounce units. Eligibility/holding durations can differ between rules;
reports explicitly disclose that this is not matched-risk account performance.
The report includes configuration, runner and data digests. Keep comparison
selection on training data; final qualification remains the existing chronological
validation and prospective process.

## What counts

Cycle completion alone is not learning. An autonomous finding requires both its
computation and its interpretation to carry server-assigned autonomous provenance.
Older records retain unknown provenance. Software releases and paper experiments
remain distinct from independently validated trading results.

Prospective attribution starts on deployment's next valid market tick. Historical
balances/fills, account state and risk settings are preserved. A review or a new
hypothesis never clears a stop or overrides stale quotes, market hours, exposure
or loss limits. Review sample thresholds are descriptive, never promotion gates.

## Verification results

- Full suite: 970 passed, 1 skipped; ten new regressions fail on 6b17513.
- Browser: desktop/mobile, visible learning counters, inert transcript text,
  bounded paging/download and no JavaScript errors.
- Real tc02: 1,000 training rows, 76 closed trades per diagnostic rule; shared
  data and runner hashes, opposite gross and equal-cost arithmetic verified.
  Compressed payload 89,033 bytes; measured transport wall time 9.571 seconds.
  Operator-directed verification only. No production account or holdout touched.

Deployment preflight preserved the main account, all four experimental account
payloads, thirteen unknown action identities and the persistent Codex thread
exactly. Deployed focused checks: 39 passed. Runtime collection starts on the
next valid quote/bar; historical attribution remains unavailable.
