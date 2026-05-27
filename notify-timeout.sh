#!/bin/sh
set -e

REPO_DIR="/Users/ken/Code/timekeepy"
ENV_FILE="$REPO_DIR/.env"
APPLESCRIPT="$REPO_DIR/notify-timeout.applescript"

# Read WORK_START_HOUR from .env (default 10 to match main.py)
WORK_START_HOUR=""
if [ -f "$ENV_FILE" ]; then
    WORK_START_HOUR=$(grep -E '^WORK_START_HOUR=' "$ENV_FILE" | tail -1 | cut -d= -f2 | tr -d "[:space:]\"'")
fi
WORK_START_HOUR=${WORK_START_HOUR:-10}

case "$WORK_START_HOUR" in
    ''|*[!0-9]*)
        echo "Invalid WORK_START_HOUR: '$WORK_START_HOUR', defaulting to 10" >&2
        WORK_START_HOUR=10
        ;;
esac

# 8-hour shift + 1h lunch buffer
TARGET_HOUR=$((WORK_START_HOUR + 9))
CURRENT_HOUR=$((10#$(date +%H)))

if [ "$1" != "force" ] && [ "$CURRENT_HOUR" -ne "$TARGET_HOUR" ]; then
    exit 0
fi

exec /usr/bin/osascript "$APPLESCRIPT"
