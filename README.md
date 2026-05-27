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

