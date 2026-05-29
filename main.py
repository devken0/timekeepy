import glob
import logging
import os
import shutil
import subprocess
import sys
import time as delay
from datetime import datetime, time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("timekeepy")

REQUIRED_ENV_VARS = [
    "WEBCAM_APP",
    "SELFIE_DIR",
    "LOGIN_URL",
    "FIRST_NAME",
    "LAST_NAME",
    "PIN",
    "SCREENSHOTS_DIR",
]


def load_config():
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        log.error("Missing required env vars: %s", ", ".join(missing))
        sys.exit(1)
    return {
        "webcam_app": os.getenv("WEBCAM_APP"),
        "selfie_dir": os.getenv("SELFIE_DIR"),
        "login_url": os.getenv("LOGIN_URL"),
        "first_name": os.getenv("FIRST_NAME"),
        "last_name": os.getenv("LAST_NAME"),
        "pin": os.getenv("PIN"),
        "screenshots_dir": os.getenv("SCREENSHOTS_DIR"),
        "work_start_hour": int(os.getenv("WORK_START_HOUR", "10")),
        "max_screenshots": int(os.getenv("MAX_SCREENSHOTS", "60")),
        "selenium_timeout_seconds": int(os.getenv("SELENIUM_TIMEOUT_SECONDS", "9999")),
        "screenshot_preview_seconds": int(os.getenv("SCREENSHOT_PREVIEW_SECONDS", "8")),
    }


def limit_files_in_directory(directory_path, max_files_limit):
    files = glob.glob(os.path.join(directory_path, "*"))
    files = [f for f in files if os.path.isfile(f)]
    files.sort(key=os.path.getmtime)

    num_files = len(files)
    if num_files <= max_files_limit:
        log.info(
            "File count (%d) is within limit (%d). No cleanup needed.",
            num_files,
            max_files_limit,
        )
        return

    files_to_remove = files[: num_files - max_files_limit]
    log.info(
        "File count (%d) exceeds limit (%d). Removing %d oldest.",
        num_files,
        max_files_limit,
        len(files_to_remove),
    )
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
            log.info("Removed: %s", file_path)
        except OSError as e:
            log.error("Error removing %s: %s", file_path, e)


def find_most_recent_jpg(folder_path):
    patterns = [
        os.path.join(folder_path, "*.[jJ][pP][gG]"),
        os.path.join(folder_path, "*.[jJ][pP][eE][gG]"),
    ]
    files = []
    for p in patterns:
        files.extend(glob.glob(p))
    files = [f for f in files if os.path.isfile(f)]

    if not files:
        return None

    return max(files, key=os.path.getmtime)


def activate_safari():
    # bring Safari to the foreground so macOS resumes rendering before screenshot capture
    try:
        subprocess.run(
            ["osascript", "-e", 'tell application "Safari" to activate'],
            check=True,
            timeout=5,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        log.warning("Could not activate Safari before screenshot: %s", e)


def preview_screenshot(screenshot_path, seconds):
    # show the saved screenshot in Quick Look, then auto-dismiss so the run stays hands-off
    if seconds <= 0:
        return
    try:
        proc = subprocess.Popen(
            ["qlmanage", "-p", screenshot_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as e:
        log.warning("Could not open Quick Look preview: %s", e)
        return
    delay.sleep(seconds)
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def main():
    config = load_config()
    os.makedirs(config["screenshots_dir"], exist_ok=True)

    # Anything older than this predates the current session (no new selfie taken).
    session_start = delay.time()

    try:
        result = subprocess.run(["open", "-a", config["webcam_app"], "-W"])
    except FileNotFoundError:
        log.error("The 'open' command or webcam app was not found.")
        sys.exit(1)
    except Exception as e:
        log.error("Error opening the webcam app: %s", e)
        sys.exit(1)

    if result.returncode != 0:
        log.error(
            "Webcam app '%s' failed to open (exit %d).",
            config["webcam_app"],
            result.returncode,
        )
        sys.exit(1)

    log.info("Application closed. Continuing script execution.")

    most_recent_file = find_most_recent_jpg(config["selfie_dir"])
    if most_recent_file is None:
        log.error("No selfie image found in %s", config["selfie_dir"])
        sys.exit(1)

    if os.path.getmtime(most_recent_file) < session_start:
        log.error(
            "Most recent selfie %s predates this session — no new photo taken?",
            most_recent_file,
        )
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    temp = f"/tmp/{timestamp}.jpg"

    try:
        shutil.move(most_recent_file, temp)
        log.info("Moved selfie: %s -> %s", most_recent_file, temp)
    except OSError as e:
        log.error("Error moving selfie file: %s", e)
        sys.exit(1)

    try:
        driver = webdriver.Safari()
        try:
            driver.get(config["login_url"])

            first_name = driver.find_element(By.ID, "firstName")
            first_name.clear()
            first_name.send_keys(config["first_name"])

            last_name = driver.find_element(By.ID, "lastName")
            last_name.clear()
            last_name.send_keys(config["last_name"])

            pin = driver.find_element(By.ID, "pin")
            pin.clear()
            pin.send_keys(config["pin"])

            login_button = driver.find_element(By.CSS_SELECTOR, ".btn-login")
            login_button.click()

            wait = WebDriverWait(driver, config["selenium_timeout_seconds"])

            dropdown_element = wait.until(EC.element_to_be_clickable((By.ID, "timeType")))
            select = Select(dropdown_element)

            current_time = datetime.now().time()
            work_start = time(config["work_start_hour"], 0, 0)
            if current_time <= work_start:
                select.select_by_visible_text("Time In")
            else:
                select.select_by_visible_text("Time Out")

            file_upload = driver.find_element(By.ID, "selfieFile")
            file_upload.send_keys(temp)

            submit = wait.until(EC.element_to_be_clickable((By.ID, "submitButton")))
            submit.click()

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-back")))

            activate_safari()
            delay.sleep(2)

            screenshot_path = os.path.join(config["screenshots_dir"], f"{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            log.info("Saved screenshot: %s", screenshot_path)

            preview_screenshot(screenshot_path, config["screenshot_preview_seconds"])
        finally:
            driver.quit()
    finally:
        try:
            os.remove(temp)
            log.info("Removed selfie temp file: %s", temp)
        except OSError as e:
            log.error("Error removing temp file %s: %s", temp, e)

    limit_files_in_directory(config["screenshots_dir"], config["max_screenshots"])


if __name__ == "__main__":
    main()
