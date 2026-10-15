#!/usr/bin/env bash
# Put the app as committed in HEAD on `jumpbox-test` on github.com, for a live run on a lab jump box.
#
#   Provisioning_Automation/alletra_onboard/scripts/push_jumpbox_test.sh   (Git Bash on Windows)
#
# The lab jump boxes cannot reach github.hpe.com, so lab runs go through the private github.com repo
# below. It carries jumpbox-test only: no releases, no main. Needs push access to that repo
# (gh auth login --hostname github.com; gh auth setup-git --hostname github.com).
#
# It builds one commit whose root is Provisioning_Automation/alletra_onboard (the layout the jump
# box expects). It never checks out, resets or commits anything locally, so it cannot touch your
# branch. Only committed work goes: commit first, including frontend/dist if the UI changed.
set -euo pipefail

APP=Provisioning_Automation/alletra_onboard
LAB_GIT=${LAB_GIT:-https://github.com/SaiHPE/Greenlake-Automation.git}
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
git push -q -f "$LAB_GIT" "$commit:refs/heads/jumpbox-test"

echo "jumpbox-test is now $branch @ ${head%% *} ($LAB_GIT)."
echo "On the jump box, paste (change the script name):"
echo '  cd $env:USERPROFILE\Downloads\alletra_onboard; git fetch origin jumpbox-test; git reset --hard origin/jumpbox-test; .\.venv\Scripts\python.exe lab\ui_live_lab.py'
