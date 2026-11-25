# KA-001 — CI environment compatibility and runner image drift

Status: corrective CI verified; artifact inventory/content inspection pending.
Observed: 2026-11-25. PR #2, head 2c7109a542f31ab5af7c7265004fb02fc8094172.
Evidence: [failed run #6](https://github.com/bg-playground/enterprise-uft-qa-lab/actions/runs/45670864079/job/139405420366).

## Expected vs actual
Expected Chromium and OS dependency installation, then SIT-008 and SIT-009 execution. Python and pip installation succeeded. The runner image was Ubuntu 26.04. Browser dependency setup reported: "Playwright does not support chromium on ubuntu26.04-x64". Browser tests were not executed and no browser artifacts existed. Windows, Linux and macOS service/HTTP jobs passed. The log reports package installation of Playwright 1.56.0 and a dependency diagnostic mentioning 1.56.1; no inference about the reason for this discrepancy is required to establish the OS incompatibility.

## Root cause and downstream impact
The floating ubuntu-latest label selected an OS unsupported by the installed browser tooling. This is an environment setup failure, not evidence of a failed application assertion. Browser and XPath coverage is unavailable for this revision. Native UFT is independently unverified.

## Alternatives and corrective action
Pin only the browser job to ubuntu-24.04, preserving the portable OS matrix, dependency pin and all assertions. Alternative: upgrade Playwright after checking the support matrix and running compatibility regression. Do not silently skip browser tests or suppress setup errors.

## BGSTM mapping
1. Test Planning: identify compatibility risk and browser coverage gate.
2. Test Case Development: preserve SIT-008/009 expected results.
3. Test Environment Preparation: explicitly select compatible runner.
4. Test Execution: retain failed run and execute new revision.
5. Test Results Analysis: distinguish setup failure, skipped tests and product defects.
6. Test Results Reporting: link both revisions and CI results; keep release decision separate.

## Acceptance and prevention
Require all four jobs successful, actual browser test execution, retained trace ZIPs and locator screenshot. Review runner and browser dependency compatibility before upgrades. A pinned OS label does not freeze every package in the runner image. Record the new run and exact head when available. No merge or deployment approval implied.

## Corrective evidence
[Run #8](https://github.com/bg-playground/enterprise-uft-qa-lab/actions/runs/45674374756), exact head ecfb45072b89057578a07a5d732ee5a95552cd8d: all four jobs successful. Browser log reports two tests in 5.388 seconds, OK. [Browser artifact](https://github.com/bg-playground/enterprise-uft-qa-lab/actions/runs/45674374756/artifacts/15050354435) uploaded, 474412 bytes, SHA256 89c27fa7cc4ce4ef62b56944c138ed8ab6bbd5a8e7b196ca6527929e7b940eb5. Individual archive entries not inspected. No native UFT results.
