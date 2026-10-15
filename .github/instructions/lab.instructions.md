---
applyTo: "Provisioning_Automation/alletra_onboard/lab/**"
---
# Lab scripts

- They run on a lab jump box against real arrays. Never run one, or suggest running one, unless the
  user asks; say first what it will change on the arrays.
- No prompts. Passwords come from the app's `.env` through `rc_failover_lab.lab_secret()`
  (`LAB_ARRAY_PW`, `LAB_DEFAULT_PW`). Never write a password, token or customer detail into a
  script: `jumpbox-test` is pushed to a public github.com repo.
- Import `rc_failover_lab as fl` for SSH, the app's API, saving evidence and restarting the app.
- Everything a script creates gets a `zz_<prefix>_` name, and the script removes it at the end,
  even after a failure. Check first that nothing with that prefix already exists, and stop if it does.
- Write PASS/FAIL lines and the evidence to `~\Downloads\<name>.zip`.
- Add the script to the table in `lab/README.md`.
