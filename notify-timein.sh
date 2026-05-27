#!/bin/sh
set -e

REPO_DIR="/Users/ken/Code/timekeepy"
ENV_FILE="$REPO_DIR/.env"
APPLESCRIPT="$REPO_DIR/notify-timein.applescript"

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

# Fire 10 minutes before shift start. LaunchAgent triggers at :50 of the
# previous hour, so target hour = WORK_START_HOUR - 1.
TARGET_HOUR=$((WORK_START_HOUR - 1))
if [ "$TARGET_HOUR" -lt 0 ]; then
    TARGET_HOUR=23
fi

CURRENT_HOUR=$((10#$(date +%H)))

if [ "$1" != "force" ] && [ "$CURRENT_HOUR" -ne "$TARGET_HOUR" ]; then
    exit 0
fi

exec /usr/bin/osascript "$APPLESCRIPT"
