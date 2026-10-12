#!/usr/bin/env bash
# Push the current commit to main, retrying if another workflow pushed first.
#
# A push that touches shared files (e.g. scripts/validate_site.py) starts many
# workflows at once, and they all try to push within seconds of each other.
# The loser is rejected. Re-basing onto the new main and pushing again fixes
# that. A genuine conflict (both changed the same lines) is not retried.
set -u

MAX_ATTEMPTS=4

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  if ! git pull --rebase origin main; then
    echo "Rebase onto main failed (real conflict) - not retrying."
    git rebase --abort 2>/dev/null || true
    exit 1
  fi

  if git push origin HEAD:main; then
    exit 0
  fi

  if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
    wait_seconds=$(( (RANDOM % 10) + 5 ))
    echo "Push rejected (another workflow pushed first). Retry $attempt/$((MAX_ATTEMPTS - 1)) in ${wait_seconds}s."
    sleep "$wait_seconds"
  fi
done

echo "Push still rejected after $MAX_ATTEMPTS attempts."
exit 1
