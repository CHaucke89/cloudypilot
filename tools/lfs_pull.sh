#!/usr/bin/env bash
# git lfs pull from the Gitea mirror in .lfsconfig, then from GitHub for anything the mirror
# hasn't synced yet (a push is only on Gitea after its next mirror sync). Arguments go to git lfs pull.
#
# Set CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET to send a Cloudflare Access service token,
# for when the LFS path is protected by a Service Auth policy instead of a Bypass policy.
set -euo pipefail

GITHUB_LFS_URL="https://github.com/CHaucke89/cloudypilot.git/info/lfs"
ROOT="$(git rev-parse --show-toplevel)"

args=()
if [ -n "${CF_ACCESS_CLIENT_ID:-}" ] && [ -n "${CF_ACCESS_CLIENT_SECRET:-}" ]; then
  LFS_URL="$(git config -f "$ROOT/.lfsconfig" lfs.url)"
  LFS_ORIGIN="$(echo "$LFS_URL" | sed -E 's|^(https?://[^/]+)/.*|\1/|')"
  args+=(-c "http.$LFS_ORIGIN.extraHeader=CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID")
  args+=(-c "http.$LFS_ORIGIN.extraHeader=CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET")
fi

if ! git ${args[@]+"${args[@]}"} lfs pull "$@"; then
  echo "LFS pull from the Gitea mirror failed, fetching what's missing from GitHub" >&2
  git -c lfs.url="$GITHUB_LFS_URL" lfs pull "$@"
fi
