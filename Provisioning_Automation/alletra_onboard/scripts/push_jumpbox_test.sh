#!/usr/bin/env bash
# Put the app as committed in HEAD on `jumpbox-test`, for a live run on a lab jump box.
#
#   scripts/push_jumpbox_test.sh            (from anywhere in the full repo; Git Bash on Windows)
#
# The jump boxes cannot reach github.hpe.com, so by default this writes to a small git store on this
# laptop (~/lab-relay, created on first use). Share that folder into the Remote Desktop session and
# labrat fetches from it with lab\fetch.ps1 (README, *A live run on a jump box*). REMOTE=<git remote>
# pushes to a git remote instead.
#
# It builds one commit whose root is Provisioning_Automation/alletra_onboard (the layout the jump
# box expects). It never checks out, resets or commits anything locally, so it cannot touch your
# branch. Only committed work goes: commit first, including frontend/dist if the UI changed.
set -euo pipefail

APP=Provisioning_Automation/alletra_onboard
RELAY=${LAB_RELAY:-$HOME/lab-relay}
cd "$(git rev-parse --show-toplevel)"

if ! git cat-file -e "HEAD:$APP" 2>/dev/null; then
  echo "HEAD has no $APP. Run this from the full repo (main or a feature branch)." >&2
  exit 1
fi
# -w: on macOS the Windows line endings show every file as changed; only real edits count here
if [ -n "$(git diff -w HEAD -- "$APP" | head -1)" ]; then
  echo "You have uncommitted changes under $APP. Commit them first; only HEAD is sent:" >&2
  git diff -w --stat HEAD -- "$APP" | tail -5 >&2
  exit 1
fi
untracked=$(git ls-files --others --exclude-standard -- "$APP")
if [ -n "$untracked" ]; then
  echo "Note: these untracked files are NOT sent:" >&2
  echo "$untracked" | head -10 >&2
fi

head=$(git log -1 --format='%h %s')
branch=$(git rev-parse --abbrev-ref HEAD)
who=$(git config user.name || echo unknown)
commit=$(git commit-tree "$(git rev-parse "HEAD:$APP")" -m "jumpbox-test: $branch $head (pushed by $who)")

if [ -n "${REMOTE:-}" ]; then
  git push -q -f "$REMOTE" "$commit:refs/heads/jumpbox-test"
  where=$(git remote get-url "$REMOTE")
else
  [ -f "$RELAY/HEAD" ] || git init -q --bare "$RELAY"
  git push -q -f "$RELAY" "$commit:refs/heads/jumpbox-test"
  where=$RELAY
fi

echo "jumpbox-test is now $branch @ ${head%% *} (in $where)."
echo "On the jump box, in the Remote Desktop session that shares that folder, paste (change the script name):"
echo '  cd $env:USERPROFILE\Downloads\alletra_onboard; .\lab\fetch.ps1; .\.venv\Scripts\python.exe lab\ui_live_lab.py'
