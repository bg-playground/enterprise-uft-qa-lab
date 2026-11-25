# Independent evidence inspection — run 14
PR head ccd3afa790d24a4c677c598c5a5c89cf05f15b34; CI checkout merge c2feaa46dd482152b7290aab280c2475e0819d16.
Run https://github.com/bg-playground/enterprise-uft-qa-lab/actions/runs/45680438064
Downloaded all four ZIP archives, opened JSON, verified SHA-256 against GitHub metadata, checked unique IDs, nonnegative durations, requirement references, counts and consistent checkout SHA.
- Linux 15054045800: 12 passed, 0 failed/skipped; results/portable.json and defects/SIT-011.json.
- Windows 15053936674: same counts and entries.
- macOS 15054141305: same counts and entries.
- Browser 15054725626: 2 passed, 0 failed/skipped; results/browser.json, browser/locator-drift.png and both trace ZIPs.
38 method executions; 14 distinct methods. Linux defect JSON confirms detection and control success. Screenshot and trace entries present, not independently replayed. No live BGSTM ingestion. Follow-up candidate adds local evidence validation and PR head metadata separately from CI checkout SHA.
