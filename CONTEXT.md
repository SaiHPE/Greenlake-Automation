# Alletra Onboard

Operator automation for onboarding an HPE Alletra MP B10000 into HPE GreenLake + DSCC. This
glossary fixes the language of the domain so code, UI, and docs use the same words.

## Language

**Post-init verification**:
After the operator confirms the array is initialized (the DSCC Set Up System wizard submitted),
logging into the array directly to confirm its configuration is correct.

**On-array config**:
The array's actual running configuration, read from the array itself. This — not the cloud's
record — is what post-init verification checks.
_Avoid_: live config, applied config

**DSCC-applied config**:
The configuration the DSCC cloud console records as having pushed to the array. Distinct from
on-array config; the two can disagree (e.g. DSCC reports "applied" but the array didn't take a value).

**Array admin credential**:
The array's local superuser account (username + password, e.g. `3paradm`) used to log into the
array directly. The same account the operator registers as the DSCC System Credential.
_Avoid_: secret, DSCC credential
