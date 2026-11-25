# DocumentFlow QA Lab
A BGSTM-driven enterprise document lifecycle testing lab. **Local prototype, not a production-ready service.** Synthetic data only. No affiliation with OpenText or any employer.

## Quick start
Python 3.12 recommended. Run `python -m pip install -r requirements.txt`, then `python app.py` and open http://127.0.0.1:8000. Submit a synthetic alphanumeric document ID and title, reenter ID and process to archive. View JSON at `/api/records` and `/api/audit`; PDF at `/api/pdf/DOC1` if DOC1 is archived.

Run `python -m unittest discover -s tests -v`. See [quality plan](docs/quality-plan.md). Service and loopback HTTP integration tests are included; see [integration acceptance](docs/integration-acceptance.md). Browser tests and an isolated locator drift exercise are included; native UFT execution remains pending. See [browser and XPath lab](docs/browser-xpath-lab.md) for execution and evidence. Cross-platform CI is configured; inspect actual workflow results.

## Native UFT track
`automation/uft/launch.vbs` is an unverified AOM starter, not a native UFT test or execution result. On a compatible licensed Windows machine, create and save a GUI test in UFT IDE, configure Web add-in and supported browser, then run the adapter with the test and results directory as two arguments. Inspect native results and record engine/version/environment. No native execution, object repository, or verified XPath support is claimed.

## Boundaries
This prototype binds loopback only and lacks authentication, comprehensive concurrency validation, retention, indexing, physical printing and production hardening. Do not expose it publicly as-is. Keep data and results synthetic.
