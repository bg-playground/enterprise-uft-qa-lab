# Integration acceptance candidate (BGSTM phases 1–6)

Planning: prioritize duplicate archival, invalid HTTP inputs and end-to-end record consistency. Code review found a read-before-write race and missing explicit connection closure. These are review findings, not claimed reproduced failures.

Case development: SIT-005 A–C shared CSV lifecycle; SIT-006 malformed/invalid HTTP and no mutation; SIT-007 simultaneous retry with four clients and one archival event.

Environment: loopback ephemeral port, isolated temporary SQLite database per test, Python 3.12 CI matrix. CSV is an engine-neutral input contract, not an executed UFT Data Table.

Execution: python -m unittest discover -s tests -v. Existing CI at 9c8cec7 passed all three operating systems (run 45651998223). New candidate requires independent CI evidence.

Analysis: BEGIN IMMEDIATE serializes archival transactions; verify no duplicate audit events. Header and digest checks establish byte integrity, not PDF semantic correctness. Explicit HTTP validation and connection cleanup are included. No production security claim.

Reporting: retain CI results per revision; browser, PDF text extraction, XPath and native UFT execution remain pending. No merge or deployment authorization implied.
