# CLAUDE.md

Personal macOS timekeeping automation. A single Python script ([main.py](main.py)) drives Safari via Selenium to clock in/out of a work web form, plus two macOS LaunchAgents that pop AppleScript dialogs as reminders.

## Run / install

```sh
./run.command              # bootstraps venv, installs requirements.txt, runs main.py
./install-schedule.sh      # generates + loads both LaunchAgents into ~/Library/LaunchAgents
./notify-timein.sh force   # smoke-test the time-in dialog (bypasses hour gate)
./notify-timeout.sh force  # smoke-test the time-out dialog (bypasses hour gate)
```

No test suite, no linter, no CI. Manual smoke-tests only.

## Configuration

All config comes from `.env` (loaded by `python-dotenv` in [main.py:16](main.py#L16)). `.env.example` is the source of truth for variable names. Required: `WEBCAM_APP`, `SELFIE_DIR`, `LOGIN_URL`, `FIRST_NAME`, `LAST_NAME`, `PIN`, `SCREENSHOTS_DIR`. Optional: `WORK_START_HOUR` (default `10`), `MAX_SCREENSHOTS` (default `60`), `SELENIUM_TIMEOUT_SECONDS` (default `9999`), `SCREENSHOT_PREVIEW_SECONDS` (default `8`; `0` disables the post-run Quick Look preview).

`WORK_START_HOUR` is the pivot for everything time-related — `main.py` uses it to choose Time In vs Time Out ([main.py:164-169](main.py#L164-L169)), and the notify wrappers read it at fire time to gate their dialogs. Change `WORK_START_HOUR` and the next day's reminders shift automatically without reinstalling the LaunchAgents.

## Architecture

**`main.py`** is a single linear `main()` function — opens the webcam app and waits for it to quit, grabs the most recent `.jpg` from `SELFIE_DIR`, moves it to `/tmp/<timestamp>.jpg`, then drives Safari through login → action dropdown → file upload → submit → screenshot. Action is picked by clock time vs `WORK_START_HOUR` (≤ start → Time In, else Time Out). After saving the screenshot it pops the image in Quick Look (`qlmanage -p`) for `SCREENSHOT_PREVIEW_SECONDS` as a non-blank confirmation, auto-dismissing by terminating that process — this replaced an old fixed `sleep(10)`. Finishes by deleting the temp selfie and pruning `SCREENSHOTS_DIR` to `MAX_SCREENSHOTS`.

**Reminder chain** (each step is its own file, all under repo root):

```
LaunchAgent .plist  →  notify-*.sh (hour gate)  →  notify-*.applescript (dialog)  →  run.command  →  main.py
                                                                          ↘ (timeout only) snooze.sh
```

LaunchAgents fire every hour in a wide window (time-in: `:50` of 5–13, time-out: `:00` of 15–22). The `.sh` wrappers compute `TARGET_HOUR` from `WORK_START_HOUR` and `exit 0` silently on non-matching hours — that's how a single installed agent tracks an editable `.env` value. `snooze.sh` is fire-and-forget `nohup sleep N; notify-timeout.sh force` (no persistence; lost on reboot/logout).

## Conventions

- Python 3, stdlib + `selenium` + `python-dotenv` only.
- 4-space indent, double-quoted strings, snake_case, module-level `log = logging.getLogger("timekeepy")`, `log.info(...) / log.error(...)` with `%s` lazy formatting (not f-strings).
- Config is read once via `load_config()` and passed around as a dict; no globals beyond `log`.
- Shell scripts: POSIX `sh` (not bash), `set -e`, `cd "$(dirname "$0")"` at top, `10#$(date +%H)` to force base-10 (avoid leading-zero octal parsing).
- AppleScripts wrap `display dialog` in `try ... on error errNum`, swallowing `-128` (user cancelled).

## Gotchas

- **Safari needs Develop → Allow Remote Automation enabled** for `webdriver.Safari()` to work. Not enforced in code — failure surfaces as a Selenium session error on startup.
- **`activate_safari()` before screenshot is load-bearing.** macOS pauses rendering for background windows, so `driver.save_screenshot()` captures a blank frame unless Safari is foregrounded first ([main.py:99-108](main.py#L99-L108), [main.py:179-180](main.py#L179-L180)). Don't remove it.
- **The Time In/Out boundary is inclusive on Time In.** `current_time <= work_start` — exactly at `WORK_START_HOUR:00:00` you clock in, not out.
- **Hard-coded `/Users/ken/Code/timekeepy` paths** in [install-schedule.sh](install-schedule.sh), [notify-timein.sh](notify-timein.sh), [notify-timeout.sh](notify-timeout.sh), [snooze.sh](snooze.sh), and both `.applescript` files. Relocating the repo means search-replacing all of them and re-running `install-schedule.sh`.
- **`open -a WEBCAM_APP -W` blocks** until the user quits the webcam app — that's intentional (script pauses while you take the selfie). Don't add a timeout.
- **`SELENIUM_TIMEOUT_SECONDS` defaults to 9999** because the user takes the selfie manually between Selenium steps. A "normal" 30s timeout will break the flow.
- **`run.command` upgrades packages on every run** (`pip install --upgrade -r requirements.txt`). Slow but tolerated; don't "fix" without checking with the user.
- **Generated `.plist` files are committed** to the repo (`com.ken.timekeepy.*-notify.plist`) but are also overwritten by `install-schedule.sh` on each install. Treat them as build artifacts that happen to be tracked.
- `.env` and `venv/` are gitignored; `.DS_Store` is gitignored too. Don't commit the user's real `.env`.
