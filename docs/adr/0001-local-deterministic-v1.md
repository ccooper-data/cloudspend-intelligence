# ADR 0001: Local, deterministic anomaly detection for V1

- Status: Accepted
- Date: 2026-10-25

## Context

The portfolio project must be useful and reviewable without a billing account, cloud credentials, or paid APIs. Cost alerts also need protection against tiny but statistically large changes. An LLM would add cost, nondeterminism, and evidence-grounding risk to a task that can be explained directly from query results.

## Decision

V1 runs in Python and SQLite over explicitly synthetic data. **Flag a service when daily cost exceeds its trailing 14-day median by both 50% and $25.** Both comparisons are strict (`>`), the current day is excluded, and exactly 14 prior daily service totals are required. A zero median and a new service are not flagged.

The explainer uses only detector output plus the largest same-day project/SKU contributor. Ties are resolved by project ID then SKU, ascending, making output repeatable. No generative AI is used in V1.

## Consequences

- The demo is free, offline, testable, and byte-for-byte repeatable.
- Median baselines tolerate isolated outliers better than means.
- New services need 14 full days before evaluation; a separate new-service policy may be added later.
- V1 detects service-level spikes and attributes the largest project/SKU contributor, but does not claim causality.
- A future optional Gemini summary must remain behind a feature flag; the deterministic explanation remains the fallback.

