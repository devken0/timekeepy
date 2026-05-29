#!/bin/sh

set -e

cd "$(dirname "$0")"
REPO_DIR=$(pwd)

# install_agent <label> <wrapper_path> <minute> <hour1 hour2 ...>
install_agent() {
    label="$1"
    wrapper="$2"
    minute="$3"
    shift 3
    hours="$*"

    plist_name="${label}.plist"
    dest="$HOME/Library/LaunchAgents/$plist_name"

    intervals=""
    for weekday in 1 2 3 4 5; do
        for hour in $hours; do
            intervals="${intervals}        <dict>
            <key>Weekday</key>
            <integer>${weekday}</integer>
            <key>Hour</key>
            <integer>${hour}</integer>
            <key>Minute</key>
            <integer>${minute}</integer>
        </dict>
"
        done
    done

    cat > "$plist_name" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${wrapper}</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
${intervals}    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/${label}.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/${label}.log</string>
</dict>
</plist>
PLIST

    echo "Generated $plist_name"
    mkdir -p "$HOME/Library/LaunchAgents"
    cp "$plist_name" "$dest"

    launchctl bootout "gui/$UID" "$dest" 2>/dev/null || true
    launchctl bootstrap "gui/$UID" "$dest"

    echo "  loaded $label"
}

# Time-out: fires at :00 of hours 15..22 weekdays; wrapper exits silently
# unless current hour == WORK_START_HOUR + 9.
install_agent \
    "com.ken.timekeepy.timeout-notify" \
    "$REPO_DIR/notify-timeout.sh" \
    0 \
    15 16 17 18 19 20 21 22

# Time-in: fires at :50 of hours 5..13 weekdays; wrapper exits silently
# unless current hour == WORK_START_HOUR - 1 (so the dialog appears at
# :50 of the hour before WORK_START_HOUR, i.e. 10 minutes before shift).
install_agent \
    "com.ken.timekeepy.timein-notify" \
    "$REPO_DIR/notify-timein.sh" \
    50 \
    5 6 7 8 9 10 11 12 13

echo
echo "Smoke-test the dialogs (bypasses hour check):"
echo "  ./notify-timeout.sh force"
echo "  ./notify-timein.sh force"
echo
echo "Disable temporarily:"
echo "  launchctl bootout gui/$UID ~/Library/LaunchAgents/com.ken.timekeepy.timeout-notify.plist"
echo "  launchctl bootout gui/$UID ~/Library/LaunchAgents/com.ken.timekeepy.timein-notify.plist"
echo "Re-enable: rerun ./install-schedule.sh"
