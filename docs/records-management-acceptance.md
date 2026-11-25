# Records management service-layer candidate
Synthetic policy, not legal advice or a real records retention standard. No HTTP/UI management endpoints or authorization implemented.
- R5: classified archived records may be disposed on or after retention boundary only. SIT-012 covers day before, exact date, idempotency, PDF removal and prevention of reprocessing.
- R6: active legal hold blocks disposition even after expiration. SIT-013 covers duplicate hold, release, eventual disposition, audit sequence.
- R7: search returns only archived records, excludes queued/disposed. SIT-014 covers literal title search and invalid classification.
Policy dates injected for reproducibility; caller is trusted in local service layer. Classification is explicit, not automatic. Disposition clears active SQLite fields, not a secure erasure guarantee (database pages/backups may retain bytes). No real data. Future role authorization, HTTP/UI, migration and retention-policy governance required. CI pending.
