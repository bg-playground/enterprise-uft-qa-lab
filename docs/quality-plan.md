# BGSTM worked example — release 0.1 candidate
Source: https://github.com/bg-playground/BGSTM (canonical six phases).

1. **Test Planning:** Scope synthetic submission, queued-to-archived transition, audit and duplicate/retry integrity. High risk: duplicate output or missing archival evidence. Excludes actual printers, authorization, retention, indexing, concurrency, UFT runtime and production deployment.
2. **Test Case Development:** Trace requirements to case IDs below. Manual steps correspond to shared input IDs; later automate in browser and UFT.
3. **Test Environment Preparation:** Python 3.12 target, ReportLab dependency, fresh SQLite database per test, local loopback only. UFT needs compatible licensed Windows host and IDE-saved test.
4. **Test Execution:** python -m unittest discover -s tests -v. Native UFT and browser execution not run.
5. **Test Results Analysis:** Check database and audit evidence, PDF header and hash. A PDF header/hash is not content/layout verification. Concurrent retry behavior is unverified.
6. **Test Results Reporting:** Local service-layer smoke candidate only; no production release sign-off. Review UI, API, negative paths, concurrency and native UFT before expanding claims.

| Requirement | Case | Manual procedure / expected |
|---|---|---|
| R1 archival | SIT-001 | Submit DOC1/Invoice; see queued; process; see archived; verify PDF and audit |
| R2 sequential retry | SIT-002 | Process DOC2 twice; exactly one archived event |
| R3 duplicate submission | SIT-003 | Submit DOC3 twice; duplicate rejected, original retained |
| R4 invalid input | SIT-004 | Empty input and missing document rejected; no records created |

SAFe-style illustrative iteration: feature = reliable print-to-archive; stories R1–R4; discuss dependency on renderer and storage, estimate with team, review evidence at iteration demo. No SAFe certification or actual client process implied.

Next: HTTP integration and Playwright, seeded defect with observed failure and verified fix, parameterization CSV, XPath diagnosis, UFT IDE test and AOM run evidence, retention and roles, hosted read-only demo.
