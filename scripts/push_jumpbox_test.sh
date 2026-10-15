#!/usr/bin/env bash
# Put the app as committed in HEAD on `jumpbox-test` on github.com, for a live run on a lab jump box.
#
#   Provisioning_Automation/alletra_onboard/scripts/push_jumpbox_test.sh   (Git Bash on Windows)
#
# The lab jump boxes cannot reach github.hpe.com, so lab runs go through the PUBLIC github.com repo
# below (public so jump boxes fetch with no login; never push secrets). It carries jumpbox-test only:
# no releases, no main. Needs push access to that repo
# (gh auth login --hostname github.com; gh auth setup-git --hostname github.com).
#
# It builds one commit whose root is Provisioning_Automation/alletra_onboard (the layout the jump
# box expects), with frontend/dist freshly built from the committed frontend/src (developers never
# commit dist; needs `npm ci` in frontend/ once). It never checks out, resets or commits anything
# locally, so it cannot touch your branch. Only committed work goes: commit first.
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

stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
if [ ! -d "$APP/frontend/node_modules" ]; then
  echo "Run 'npm ci' in $APP/frontend once: this script builds frontend/dist for the jump box." >&2
  exit 1
fi
echo "Building frontend/dist from frontend/src ..."
(cd "$APP/frontend" && npx --no-install vite build --outDir "$stage/frontend/dist" --emptyOutDir --logLevel error)

# A throwaway index: HEAD's app folder with its frontend/dist swapped for the fresh build.
gd=$(git rev-parse --absolute-git-dir)
export GIT_INDEX_FILE="$stage/index"
git --git-dir="$gd" --work-tree="$stage" -C "$stage" read-tree "HEAD:$APP"
git --git-dir="$gd" --work-tree="$stage" -C "$stage" rm -r -q --cached --ignore-unmatch frontend/dist
git --git-dir="$gd" --work-tree="$stage" -C "$stage" add -f frontend/dist
tree=$(git --git-dir="$gd" write-tree)
unset GIT_INDEX_FILE

commit=$(git commit-tree "$tree" -m "jumpbox-test: $branch $head (pushed by $who)")
git push -q -f "$LAB_GIT" "$commit:refs/heads/jumpbox-test"

echo "jumpbox-test is now $branch @ ${head%% *} ($LAB_GIT)."
echo "On the jump box, paste (change the script name):"
echo '  cd $env:USERPROFILE\Downloads\alletra_onboard; git fetch origin jumpbox-test; git reset --hard origin/jumpbox-test; .\.venv\Scripts\python.exe lab\ui_live_lab.py'
