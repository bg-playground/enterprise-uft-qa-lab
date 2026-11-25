# SIT-010 — PDF semantic validation

Requirement: the archived PDF must contain the submitted document ID and title, one page, expected author/title/subject metadata and a digest matching the persisted record. Use the three synthetic CSV rows already used by HTTP and Playwright. Execute via loopback HTTP, parse bytes independently using pypdf, compare exact extracted lines and metadata, then reconcile the API record.

BGSTM: plan for wrong-template/field risks; develop SIT-010; prepare isolated database and parser; execute in portable CI; analyze content separately from digest; report exact head and results. This verifies the bounded ASCII synthetic fixtures, not visual layout, Unicode coverage, OCR or arbitrary PDF compatibility. New revision CI pending.
