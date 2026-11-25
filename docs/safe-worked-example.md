# SAFe-aligned worked example — illustrative, not client experience
Feature: reliable print-to-archive and controlled records disposition. Business value: correct output and preserved records subject to hold. Acceptance: R1–R7 traceable; no disposition before boundary or during hold; no duplicate archival; browser and API evidence.
## PI planning example
Dependencies: document rendering, records policy owner, storage, automation environment, licensed UFT host. Proposed iteration 1: lifecycle/HTTP/PDF; iteration 2: retention and hold; iteration 3: access control and browser/records integration. UFT is a separate dependency, not a portable release claim.
| Story | Relative estimate (illustrative points) | Risk | Acceptance |
|---|---:|---|---|
| Lifecycle and retries | 5 | High | SIT-001–007 |
| Browser and locator resilience | 5 | Medium | SIT-008–009 |
| PDF semantic integrity | 3 | High | SIT-010–011 |
| Retention and hold | 5 | High | SIT-012–013 |
| Search and lifecycle exclusion | 3 | Medium | SIT-014 |
| Role authorization and native UFT | TBD | High | scope and environment required |
Points are planning examples, not actual team estimates or velocity. Review with team before commitment.
## BGSTM alignment
Planning: risk, dependencies and scope at PI/iteration planning. Case development: story acceptance and traceability. Environment: isolated fixtures and runner compatibility. Execution: iteration CI and exploratory validation. Analysis: defects and downstream impact, including legal hold and archival integrity. Reporting: system demo, residual risk and release decision. Inspect/adapt: review KA-001/002 and reporting gaps. No SAFe certification claimed.
