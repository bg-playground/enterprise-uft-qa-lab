# Browser and XPath troubleshooting lab

## Run
Install Python 3.12, then:
```sh
python -m pip install -r requirements.txt -r requirements-browser.txt
python -m playwright install chromium
python -m unittest discover -s browser-tests -v
```
Linux may require browser OS dependencies (CI uses --with-deps). Tests start an isolated loopback server and temporary SQLite DB. Never use real records. Trace ZIPs and screenshot are in artifacts/browser and CI uploads them even on failure. Use python -m playwright show-trace <zip> to inspect.

## SIT-008: shared CSV
For each test-data/lifecycle.csv row submit via browser, verify queued, process, verify archived, reconcile HTTP record and PDF digest. Same test intent as SIT-005 but distinct engine and evidence. PDF semantic/layout verification remains pending.

## SIT-009: locator drift
Normal page / has button id process. Controlled /locator-lab has id archive-v2, with unchanged business action and stable data-testid archive-document. The legacy XPath //button[@id='process'] matches exactly one on normal page and zero on alternate page. Inspect DOM and screenshot; repair to //button[@data-testid='archive-document'], assert unique match, process and verify audit. Prefer accessible role/name selectors when possible. This is an intentional local exercise, not a production defect. No failing UFT execution is claimed.

## UFT translation (not executed)
On licensed compatible Windows with Web add-in, inspect the button with UFT Object Spy, evaluate whether the installed version supports XPath for the specific WebButton description, and verify unique identification before editing the repository or descriptive programming. Import the CSV into an IDE Data Table using the supported workflow; map document_id/title/expected_status and preserve case_id. Save a native test and use the existing unverified AOM launcher. Capture actual UFT version, browser, native results, and failure diagnostics. Playwright traces cannot serve as UFT evidence.

## BGSTM evidence
Planning: prioritize locator resilience and UI/API consistency. Case development: SIT-008 and SIT-009. Environment: isolated browser context and database. Execution: engine-specific CI. Analysis: inspect locator counts and audit, distinguish intentional mismatch from real failure. Reporting: attach trace and screenshot, record exact revision and run, with separate UFT status. New candidate not accepted until CI is verified.
