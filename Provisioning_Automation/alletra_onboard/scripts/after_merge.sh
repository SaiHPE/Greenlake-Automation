#!/usr/bin/env bash
# The owner's one command after merging pull requests on github.hpe.com.
#
#   Provisioning_Automation/alletra_onboard/scripts/after_merge.sh [--no-release] [--lab]
#
# 1. updates local main from origin (fast-forward only; refuses local changes)
# 2. rebuilds frontend/dist from frontend/src; if it differs, commits and pushes it to main
#    (developers never commit dist; this also overwrites anything a branch slipped in)
# 3. refreshes jumpbox-package on github.hpe.com (subtree split of the app folder)
# 4. refreshes the rolling `latest` release zip (scripts/publish_release.ps1; skip: --no-release)
# 5. --lab: also puts main on jumpbox-test, so the lab jump boxes can run released code
# Needs: git with `git subtree`, Node 20 with `npm ci` done in frontend/, gh and pwsh for step 4.
set -euo pipefail

APP=Provisioning_Automation/alletra_onboard
release=1 lab=0
for arg in "$@"; do
  case "$arg" in
    --no-release) release=0 ;;
    --lab) lab=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done
cd "$(git rev-parse --show-toplevel)"

[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || { echo "Switch to main first: git switch main" >&2; exit 1; }
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "main has local changes; commit or stash them first:" >&2
  git status --short --untracked-files=no | head -10 >&2
  exit 1
fi
# GitHub Desktop's git lacks `subtree`; Apple's /usr/bin/git and Homebrew git have it.
has_subtree() { case "$("$1" subtree -h 2>&1 || true)" in *"git subtree"*) return 0 ;; *) return 1 ;; esac; }
SUBTREE_GIT=git
if ! has_subtree git; then
  if [ -x /usr/bin/git ] && has_subtree /usr/bin/git; then
    SUBTREE_GIT=/usr/bin/git
  else
    echo "git subtree is missing: the git on PATH lacks it (GitHub Desktop's does). Install Homebrew git, or put /usr/bin first on PATH." >&2
    exit 1
  fi
fi

echo "== 1. main from origin"
git pull -q --ff-only origin main
git log -1 --format='   %h %s'

echo "== 2. frontend/dist"
fe="$APP/frontend"
[ -d "$fe/node_modules" ] || { echo "Run 'npm ci' in $fe once." >&2; exit 1; }
if [ "$fe/package-lock.json" -nt "$fe/node_modules/.package-lock.json" ]; then
  (cd "$fe" && npm ci --no-audit --no-fund --loglevel=error)
fi
(cd "$fe" && npm run -s build >/dev/null)
if [ -n "$(git status --porcelain -- "$fe/dist")" ]; then
  git add -A -- "$fe/dist"
  ALLOW_DIST=1 git commit -q -m "Rebuild frontend/dist from main @ $(git rev-parse --short HEAD)"
  git push -q origin main
  echo "   rebuilt and pushed: $(git log -1 --format=%h)"
else
  echo "   already matches frontend/src"
fi

echo "== 3. jumpbox-package"
"$SUBTREE_GIT" subtree split -q --prefix="$APP" -b jbp-new
git branch -f jumpbox-package jbp-new && git branch -D -q jbp-new
git push -q -f origin jumpbox-package
echo "   $(git rev-parse --short jumpbox-package)"

if [ "$release" = 1 ]; then
  echo "== 4. latest release zip"
  (cd "$APP" && pwsh -NoProfile -File scripts/publish_release.ps1)
fi

if [ "$lab" = 1 ]; then
  echo "== 5. jumpbox-test"
  "$APP/scripts/push_jumpbox_test.sh"
fi
echo "Done."
