import subprocess
import time as delay 
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from datetime import datetime, time

# load environment variables
load_dotenv()

def limit_files_in_directory(directory_path, max_files_limit):
  # get list of all files in the directory
  files = glob.glob(os.path.join(directory_path, '*'))
  files = [f for f in files if os.path.isfile(f)]

  # sort files by modification time
  files.sort(key=os.path.getmtime)

  # check if number of files exceed the limit
  num_files = len(files)
  if num_files > max_files_limit:
    files_to_remove_count = num_files - max_files_limit
    files_to_remove = files[:files_to_remove_count]

    print(f"Current file count ({num_files}) exceeds limit ({max_files_limit}).")
    print(f"Removing {files_to_remove_count} oldest files.")

    # remove the oldest files
    for file_path in files_to_remove:
      try:
        os.remove(file_path)
        print(f"Removed: {file_path}")
      except OSError as e:
        print(f"Error removing {file_path}: {e}")
  else:
    print(f"Current file count ({num_files}) is within the limit of ({max_files_limit}) files. No action needed.")
    
def find_most_recent_jpg(folder_path):
  # Create a pattern to match .jpg and .jpeg files (case-insensitive)
  # The pattern should include the full path
  search_pattern = os.path.join(folder_path, '*.[jJ][pP][gG]')

  # returns a list of paths
  list_of_files = glob.glob(search_pattern)

  # Ensure the list only contains actual files (not directories, although glob usually handles this)
  files = [f for f in list_of_files if os.path.isfile(f)]

  if not files:
    return None # No .jpg or .jpeg files found

  # find the most recent image
  latest_file = max(files, key=os.path.getmtime)

  return latest_file

def activate_safari():
  try:
    subprocess.run(
      ["osascript", "-e", 'tell application "Safari" to activate'],
      check=True,
      timeout=5,
    )
  except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
    print(f"Warning: could not activate Safari before screenshot: {e}")

try:
  # open app
  app_name = os.getenv("WEBCAM_APP") 
  process = subprocess.run(["open", "-a", app_name, '-W'])
except FileNotFoundError:
   print("The application was not found.")
except Exception as e:
   print(f"An error occured: {e}")

print("Application closed. Continuing Python script execution.")

# scan directory for new selfie image
directory_to_scan = os.getenv("SELFIE_DIR") 
most_recent_file = find_most_recent_jpg(directory_to_scan)

# mv the new selfie image
source = most_recent_file
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
temp = f'/tmp/{timestamp}.jpg' # rename the file to have the current date and time
destination = temp 

try: 
  subprocess.run(["mv", source, destination], check=True)
  print(f"Executed mv command: mv {source} {destination}")
except subprocess.CalledProcessError as e:
  print(f"Error executing mv command: {e}")
except FileNotFoundError:
  print("Error: 'mv' command not found.")

# initialize safari webdriver
driver = webdriver.Safari()

# employee login/timekeeping url

driver.get(os.getenv("LOGIN_URL"))

first_name = driver.find_element(By.ID, "firstName")
first_name.clear()
first_name.send_keys(os.getenv("FIRST_NAME"))

last_name = driver.find_element(By.ID, "lastName")
last_name.clear()
last_name.send_keys(os.getenv("LAST_NAME"))

pin = driver.find_element(By.ID, "pin")
pin.clear()
pin.send_keys(os.getenv("PIN"))

login_button = driver.find_element(By.CSS_SELECTOR, ".btn-login")
login_button.click()

timeout = 9999 

wait = WebDriverWait(driver, timeout) 

dropdown_element = wait.until(EC.element_to_be_clickable((By.ID, "timeType")))
select = Select(dropdown_element)

# get current time of day
current_time = datetime.now().time()

# define specific time (start of work) - 10 AM
work_start = time(10, 0, 0) 

if current_time <= work_start:
  select.select_by_visible_text("Time In")
else: 
  select.select_by_visible_text("Time Out")
  
fileUpload = driver.find_element(By.ID, "selfieFile")
fileUpload.send_keys(temp)

submit = wait.until(EC.element_to_be_clickable((By.ID, "submitButton")))
submit.click()

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-back")))

# bring Safari to the foreground so macOS resumes rendering before capture
activate_safari()
delay.sleep(2)

screenshots_dir = f"{os.getenv('SCREENSHOTS_DIR')}"

# save screenshot
driver.save_screenshot(f"{screenshots_dir}/{timestamp}.png")

delay.sleep(10)

driver.quit()

# cleanup
# delete selfie
command = ['rm', temp]
subprocess.run(command)
print(f"Executed rm command: rm {temp}")

# limit screenshots to 60
directory_to_manage = f'{screenshots_dir}' 
max_allowed_files = 60
limit_files_in_directory(directory_to_manage, max_allowed_files)
