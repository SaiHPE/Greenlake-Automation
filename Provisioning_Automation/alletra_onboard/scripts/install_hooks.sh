#!/usr/bin/env bash
# Turns on the repository's git hooks for this clone (once per clone; Git Bash on Windows):
#
#   Provisioning_Automation/alletra_onboard/scripts/install_hooks.sh
#
#   .githooks/pre-commit  refuses a commit that changes frontend/dist or holds a token or private key
#   .githooks/pre-push    runs scripts/check.py and refuses a push that does not say PASS
#
# It sets core.hooksPath to .githooks, the same setting the pre-commit hook always used, so running
# it again or on a clone that already has the setting changes nothing.
set -euo pipefail

APP=Provisioning_Automation/alletra_onboard
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
echo "Git hooks on: core.hooksPath = $(git config core.hooksPath) ($(ls .githooks | tr '\n' ' '))"

if [ ! -x "$APP/.venv/bin/python" ] && [ ! -x "$APP/.venv/Scripts/python.exe" ]; then
  echo "Note: $APP/.venv is missing, so pre-push will refuse every push until you create it:" >&2
  echo "  cd $APP && python -m venv .venv && .venv/bin/pip install -e \".[dev]\"" >&2
  echo "  (or set CHECK_PYTHON to a Python that has the app installed)" >&2
fi
