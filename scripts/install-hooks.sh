#!/bin/sh
# Install only repository-local Git hook configuration; never overwrite custom hooks.
set -eu
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"
existing=$(git config --get core.hooksPath || :)
case "$existing" in
  '')
    default_hooks=$(git rev-parse --git-path hooks)
    for hook in "$default_hooks"/*; do
      case "$hook" in *.sample) continue ;; esac
      if [ -f "$hook" ] && [ -x "$hook" ]; then
        printf '%s\n' 'Refusing to disable existing executable default Git hooks.' >&2
        exit 1
      fi
    done
    ;;
  .githooks|"$repo_root/.githooks") ;;
  *) printf '%s\n' 'Refusing to replace an existing custom core.hooksPath.' >&2; exit 1 ;;
esac
command -v python3 >/dev/null 2>&1 || {
  printf '%s\n' 'Python 3 is required; install it through the dotfiles package policy.' >&2
  exit 1
}
test -f scripts/public_repo_guard.py
test -f .githooks/pre-commit
test -f .githooks/pre-push
chmod +x .githooks/pre-commit .githooks/pre-push
git config --local core.hooksPath .githooks
printf '%s\n' 'Enabled local pre-commit and pre-push public repository guards.'
