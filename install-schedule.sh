#!/bin/sh

set -e

cd "$(dirname "$0")"

PLIST_NAME="com.ken.timekeepy.timeout-notify.plist"
LABEL="com.ken.timekeepy.timeout-notify"
DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"
WRAPPER="/Users/ken/Code/timekeepy/notify-timeout.sh"

# Hours (24h) on which to fire the wrapper each weekday. The wrapper reads
# WORK_START_HOUR from .env and exits silently unless the current hour matches
# WORK_START_HOUR + 9, so this just needs to be a superset of plausible target
# hours. 15..22 covers WORK_START_HOUR values 6..13.
HOURS="15 16 17 18 19 20 21 22"

INTERVALS=""
for weekday in 1 2 3 4 5; do
    for hour in $HOURS; do
        INTERVALS="${INTERVALS}        <dict>
            <key>Weekday</key>
            <integer>${weekday}</integer>
            <key>Hour</key>
            <integer>${hour}</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
"
    done
done

cat > "$PLIST_NAME" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${WRAPPER}</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
${INTERVALS}    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/timekeepy-timeout-notify.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/timekeepy-timeout-notify.log</string>
</dict>
</plist>
PLIST

echo "Generated $PLIST_NAME"
echo "Copying $PLIST_NAME -> $DEST"
mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_NAME" "$DEST"

echo "Unloading any existing instance (ignored if not loaded)..."
launchctl bootout "gui/$UID" "$DEST" 2>/dev/null || true

echo "Loading LaunchAgent..."
launchctl bootstrap "gui/$UID" "$DEST"

echo
echo "Installed. Job status:"
launchctl print "gui/$UID/$LABEL" | grep -E "state|runs" || true

echo
echo "To smoke-test the dialog now (forces wrapper to run regardless of hour):"
echo "  $WRAPPER force"
echo
echo "To trigger the LaunchAgent (still gated by current hour vs WORK_START_HOUR + 9):"
echo "  launchctl kickstart -k gui/$UID/$LABEL"
echo
echo "To disable temporarily:"
echo "  launchctl bootout gui/$UID $DEST"
echo "To re-enable:"
echo "  launchctl bootstrap gui/$UID $DEST"
