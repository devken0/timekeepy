#!/bin/sh
# Background a delayed re-fire of the time-out reminder.
# Usage: snooze.sh [minutes]   (default 10)

MINUTES="${1:-10}"
SECONDS_DELAY=$((MINUTES * 60))

REPO_DIR=$(cd "$(dirname "$0")" && pwd)

nohup sh -c "sleep $SECONDS_DELAY; \"$REPO_DIR/notify-timeout.sh\" force" </dev/null >/dev/null 2>&1 &
