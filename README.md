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

### Scheduled reminders

Two LaunchAgents nudge you Mon–Fri so you don't forget to clock in or out. Both derive their fire time from `WORK_START_HOUR` in `.env` — edit that value and the next day's reminders shift automatically (no reinstall).

**Time-in reminder** — fires 10 minutes before shift start (e.g. 09:50 for `WORK_START_HOUR=10`). Dialog: *"Time to time in for your shift?"* with **Ignore** and **Time in now**. No snooze: snoozing would just make you late.

**Time-out reminder** — fires at `WORK_START_HOUR + 9` (8h shift + 1h lunch; e.g. 19:00 for `WORK_START_HOUR=10`). Dialog: *"Have you already timed out for today?"* with **Ignore**, **Remind in 10 min**, and **Time out now**. The 10-minute snooze is short on purpose — overtime is unpaid, so a single snooze keeps you well under typical timesheet rounding.

Both *Time in now* / *Time out now* buttons launch `run.command`; `main.py` picks the right action based on current time.

Install both:

```sh
./install-schedule.sh
```

Smoke-test the dialogs without waiting (bypasses the hour check):

```sh
./notify-timein.sh force
./notify-timeout.sh force
```

Disable temporarily (e.g. PTO):

```sh
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.ken.timekeepy.timein-notify.plist
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.ken.timekeepy.timeout-notify.plist
```

Re-enable: rerun `./install-schedule.sh`.

Logs: `/tmp/com.ken.timekeepy.timein-notify.log`, `/tmp/com.ken.timekeepy.timeout-notify.log`.

