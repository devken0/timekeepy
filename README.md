This is a simple timekeeping tool that I use at work. It uses python libraries like Selenium to automate interaction with the web browser. It helped me learn how to create simple scripts to improve daily tasks.

### Usage

1. Copy `.env.example` to `.env` and fill in the required values.
2. Execute `run.command`.
3. Take a photo.
4. Quit the app.
5. Wait for the script to finish.

### Optional env vars

`.env.example` documents three optional overrides:

- `WORK_START_HOUR` (default `10`) — hour-of-day cutoff between "Time In" and "Time Out".
- `MAX_SCREENSHOTS` (default `60`) — cap on screenshots kept in `SCREENSHOTS_DIR`.
- `SELENIUM_TIMEOUT_SECONDS` (default `9999`) — how long Selenium waits for elements (kept high because you take the selfie manually between steps).

### Scheduled reminder

A LaunchAgent can prompt you Mon–Fri at the end of your shift with *"Have you already timed out for today?"* and three buttons: **Ignore**, **Remind in 10 min**, and **Time out now** (which launches `run.command`). The 10-minute snooze is short on purpose — overtime is unpaid, so a single snooze keeps you well under typical timesheet rounding.

The reminder time is derived from `WORK_START_HOUR` in `.env`: it fires at `WORK_START_HOUR + 9` (8h shift + 1h lunch). With the default `WORK_START_HOUR=10` the prompt appears at 19:00. Change `WORK_START_HOUR` in `.env` and the next day's reminder moves automatically — no reinstall needed (the LaunchAgent fires hourly within a wide evening window and the wrapper re-reads `.env` each time).

Install:

```sh
./install-schedule.sh
```

Smoke-test the dialog without waiting (bypasses the hour check):

```sh
./notify-timeout.sh force
```

Disable temporarily (e.g. PTO):

```sh
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.ken.timekeepy.timeout-notify.plist
```

Re-enable:

```sh
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.ken.timekeepy.timeout-notify.plist
```

Logs: `/tmp/timekeepy-timeout-notify.log`.

