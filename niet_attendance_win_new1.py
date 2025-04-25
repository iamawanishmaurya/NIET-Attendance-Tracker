import os
import sys
import subprocess
import importlib

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text, color, bold=False, underline=False):
    """Print colored text with optional formatting."""
    format_codes = ""
    if bold: format_codes += Colors.BOLD
    if underline: format_codes += Colors.UNDERLINE
    print(f"{format_codes}{color}{text}{Colors.END}")

def print_big_message(message, color=Colors.YELLOW):
    """Print a big, prominent message."""
    width = len(message) + 4
    print_colored("="*width, color, bold=True)
    print_colored(f"  {message}  ", color, bold=True)
    print_colored("="*width, color, bold=True)

def install_package(package_name):
    """Install a package using pip."""
    try:
        print_colored(f"Installing {package_name}...", Colors.CYAN)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"Failed to install {package_name}: {str(e)}", Colors.RED)
        return False

def is_package_installed(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def check_and_install_packages():
    """Check and install required packages if missing."""
    # First, ensure setuptools is installed
    if not is_package_installed('pkg_resources'):
        print_colored("Installing setuptools...", Colors.CYAN)
        if not install_package('setuptools'):
            print_colored("Failed to install setuptools. Please install it manually: pip install setuptools", Colors.RED)
            sys.exit(1)
        print_big_message("Please restart the script to continue")
        sys.exit(0)

    import pkg_resources

    required_packages = {
        'pandas': 'pandas',
        'requests': 'requests',
        'cryptography': 'cryptography',
        'rich': 'rich',
        'tabulate': 'tabulate',
        'selenium': 'selenium',
        'beautifulsoup4': 'bs4',
        'webdriver-manager': 'webdriver_manager',
        'colorama': 'colorama',
        'urllib3': 'urllib3',
        'setuptools': 'pkg_resources'
    }
    
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = []
    
    print_colored("\n=== Checking Required Packages ===", Colors.HEADER, bold=True)
    for package, import_name in required_packages.items():
        if package.lower() not in installed_packages:
            print_colored(f"❌ {package:<20} not found", Colors.RED)
            missing_packages.append(package)
        else:
            print_colored(f"✅ {package:<20} found", Colors.GREEN)
    
    if missing_packages:
        print_colored("\n=== Installing Missing Packages ===", Colors.HEADER, bold=True)
        for package in missing_packages:
            if install_package(package):
                print_colored(f"✅ Successfully installed {package}", Colors.GREEN)
            else:
                print_colored(f"❌ Failed to install {package}", Colors.RED)
        
        print("\n")
        print_big_message("Please restart the script to use newly installed packages!")
        sys.exit(0)
    else:
        print_colored("\n✅ All required packages are installed!", Colors.GREEN, bold=True)

# Run package check at startup
if __name__ == "__main__":
    try:
        # Try to enable Windows ANSI color support
        if os.name == 'nt':
            os.system('color')
            
        check_and_install_packages()
    except Exception as e:
        print_colored(f"Error during package check: {str(e)}", Colors.RED)
        print_colored("Attempting to install basic requirements...", Colors.YELLOW)
        install_package('setuptools')
        print("\n")
        print_big_message("Please restart the script to continue")
        sys.exit(1)

# --- Basic Imports ---
import json
import pandas as pd
import requests
from datetime import datetime, timedelta, date
import math
import time
import threading
import getpass # For password input
import urllib3 # To manage SSL warnings
import traceback # For detailed error printing
import platform
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Global Variables ---
RICH_AVAILABLE = False
TABULATE_AVAILABLE = False
CRYPTOGRAPHY_AVAILABLE = False
SELENIUM_AVAILABLE = False
DEBUG_MODE = False
_loading_stop = threading.Event()
_loading_thread = None

# --- Selenium for Browser Automation ---
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from bs4 import BeautifulSoup
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    SELENIUM_AVAILABLE = True
except ImportError:
    print(f"⚠️ Warning: Selenium missing. Browser login disabled. (pip install selenium beautifulsoup4 webdriver-manager)")
    class WebDriverException(Exception): pass
    class TimeoutException(Exception): pass

# --- Cryptography for Password Encryption ---
CRYPTOGRAPHY_AVAILABLE = False

# --- Rich for Table Display ---
try:
    from rich.console import Console
    from rich.table import Table
    import rich.box as box # Import box styles
    RICH_AVAILABLE = True
except ImportError:
    class Console: pass # Dummy class
    class Table: pass # Dummy class
    print("⚠️ Optional 'rich' library not found. Tables will have basic formatting. (pip install rich)")

# --- Tabulate for Table Display ---
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    def tabulate(data, headers=None, tablefmt=None, showindex=None): # Dummy function
        """Minimalistic fallback for printing table data if tabulate/rich is not installed."""
        output_lines = []
        output_lines.append("--- Table Data (tabulate/rich not installed) ---")
        col_names = []
        data_list = [] # Ensure data_list is defined

        if isinstance(data, pd.DataFrame):
             data_list = data.to_dict('records') # Convert DataFrame for consistency
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            data_list = data
        elif isinstance(data, list): # Handle list of non-dicts or empty list
            data_list = data # Keep as is for potential non-dict list handling
        else:
             output_lines.append(str(data)) # Print simple data as is
             print("\n".join(output_lines)); return

        if data_list and isinstance(data_list[0], dict): # Check if it's list of dicts
            # Use keys from the first dictionary as headers
            col_names = list(data_list[0].keys())
            # Filter out internal keys like '_style' if present
            col_names = [h for h in col_names if not h.startswith('_')]
            # Use provided headers if they exist and are not 'keys'
            if headers and headers != 'keys':
                output_lines.append(" | ".join(map(str, headers)))
            else:
                output_lines.append(" | ".join(col_names)) # Use dict keys as headers

            # Print rows using the filtered column names
            for row_dict in data_list:
                 row_values = [str(row_dict.get(h, '')) for h in col_names]
                 output_lines.append(" | ".join(row_values))
        elif data_list: # Handle list of lists or other iterables
             if headers and headers != 'keys':
                output_lines.append(" | ".join(map(str, headers)))
             for row in data_list:
                 if isinstance(row, (list, tuple)):
                     output_lines.append(" | ".join(map(str, row)))
                 else:
                     output_lines.append(str(row)) # Print individual items if not list/tuple
        else: # Handle empty list
             if headers and headers != 'keys': output_lines.append(" | ".join(map(str, headers)))
             output_lines.append("(No data rows)")

        output_lines.append("------------------------------------------------")
        print("\n".join(output_lines))


# --- Colorama for Text Colors (used by rich and fallback) ---
try:
    import colorama
    colorama.init(autoreset=True)
    C_RESET=colorama.Style.RESET_ALL; C_BRIGHT=colorama.Style.BRIGHT; C_DIM=colorama.Style.DIM
    C_RED=C_BRIGHT+colorama.Fore.RED; C_GREEN=C_BRIGHT+colorama.Fore.GREEN; C_YELLOW=C_BRIGHT+colorama.Fore.YELLOW
    C_BLUE=C_BRIGHT+colorama.Fore.BLUE; C_MAGENTA=C_BRIGHT+colorama.Fore.MAGENTA; C_CYAN=C_BRIGHT+colorama.Fore.CYAN
    C_WHITE=C_BRIGHT+colorama.Fore.WHITE; C_BLACK=C_BRIGHT+colorama.Fore.BLACK
    C_HEADER=C_BRIGHT+colorama.Fore.CYAN; C_TITLE=C_BRIGHT+colorama.Fore.MAGENTA
    C_PROMPT=C_BRIGHT+colorama.Fore.YELLOW; C_ERROR=C_BRIGHT+colorama.Fore.RED
    C_WARNING=C_BRIGHT+colorama.Fore.YELLOW; C_SUCCESS=C_BRIGHT+colorama.Fore.GREEN
    C_INFO=C_BRIGHT+colorama.Fore.BLUE; C_BOLD=C_BRIGHT
    C_LOW=C_BRIGHT+colorama.Fore.RED; C_MID=C_BRIGHT+colorama.Fore.YELLOW; C_HIGH=C_BRIGHT+colorama.Fore.GREEN
    C_SUBJECT=C_BRIGHT+colorama.Fore.MAGENTA
except ImportError:
    print("Warning: 'colorama' not installed. Styles disabled. (pip install colorama)")
    C_RESET=C_BRIGHT=C_DIM=C_RED=C_GREEN=C_YELLOW=C_BLUE=""
    C_MAGENTA=C_CYAN=C_WHITE=C_BLACK=C_HEADER=C_TITLE=""
    C_PROMPT=C_ERROR=C_WARNING=C_SUCCESS=C_INFO=C_BOLD=""
    C_LOW=C_MID=C_HIGH=C_SUBJECT=""

# --- Configuration ---
CREDENTIALS_FILE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "niet_attendance", "credentials.json")
ATTENDANCE_FILE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "niet_attendance", "attendance.json")
SELENIUM_OUTPUT_FILE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "niet_attendance", "output_login_page.html")
JSESSIONID_FILE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "niet_attendance", "jsessionid.txt")
NIET_LOGIN_URL = "https://nietcloud.niet.co.in/login.htm"
NIET_ATTENDANCE_URL = 'https://nietcloud.niet.co.in/getSubjectOnChangeWithSemId1.json'

def ensure_directory_exists():
    """Ensures the directory for storing files exists."""
    try:
        directory = os.path.dirname(CREDENTIALS_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"{C_SUCCESS}{E_SUCCESS} Created directory: {directory}{C_RESET}")
    except Exception as e:
        print(f"{C_ERROR}{E_ERROR} Could not create directory: {e}{C_RESET}")

def load_credentials():
    """Load saved credentials from file."""
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
            return [{'username': k, 'password': v} for k, v in creds.items()] if isinstance(creds, dict) else (creds if isinstance(creds, list) else [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_credentials(username, password):
    """Save credentials to file."""
    try:
        ensure_directory_exists()
        creds = load_credentials()
        # Update existing or add new using list comprehension
        if not any(cred['username'] == username and cred.update({'password': password}) for cred in creds):
            creds.append({'username': username, 'password': password})
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(creds, f, indent=4)
        print(f"{C_SUCCESS}{E_SUCCESS} Credentials saved successfully.{C_RESET}")
    except Exception as e:
        print(f"{C_ERROR}{E_ERROR} Failed to save credentials: {e}{C_RESET}")

def save_jsessionid(jsessionid):
    """Saves the JSESSIONID to a file."""
    try:
        ensure_directory_exists()
        with open(JSESSIONID_FILE, 'w', encoding='utf-8') as f:
            f.write(jsessionid)
        if DEBUG_MODE:
            print(f"{C_SUCCESS}{E_SUCCESS} JSESSIONID saved to {JSESSIONID_FILE}{C_RESET}")
    except IOError as e:
        if DEBUG_MODE:
            print(f"{C_WARNING}{E_WARNING} Could not save JSESSIONID: {e}{C_RESET}")
            print(f"{C_INFO}Please ensure you have write permissions to: {os.path.dirname(JSESSIONID_FILE)}{C_RESET}")

def load_jsessionid():
    """Loads the JSESSIONID from file if it exists."""
    try:
        ensure_directory_exists()
        if not os.path.exists(JSESSIONID_FILE):
            if DEBUG_MODE:
                print(f"{C_INFO}{E_INFO} No saved JSESSIONID found at {JSESSIONID_FILE}{C_RESET}")
            return None
        with open(JSESSIONID_FILE, 'r', encoding='utf-8') as f:
            jsessionid = f.read().strip()
        if jsessionid:
            if DEBUG_MODE:
                print(f"{C_INFO}{E_INFO} Found saved JSESSIONID at {JSESSIONID_FILE}{C_RESET}")
            return jsessionid
        else:
            if DEBUG_MODE:
                print(f"{C_WARNING}{E_WARNING} Saved JSESSIONID is empty.{C_RESET}")
            return None
    except IOError as e:
        if DEBUG_MODE:
            print(f"{C_WARNING}{E_WARNING} Could not read saved JSESSIONID: {e}{C_RESET}")
        return None

def generate_key():
    """Generates a new Fernet key and saves it to KEY_FILE."""
    if not CRYPTOGRAPHY_AVAILABLE:
        print(f"{C_ERROR}{E_ERROR} Cryptography library not found. Cannot generate key. (pip install cryptography){C_RESET}")
        return None
    try:
        ensure_directory_exists()
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(f"{C_SUCCESS}{E_KEY} New encryption key generated and saved to '{KEY_FILE}'.{C_RESET}")
        print(f"{C_WARNING} IMPORTANT: Back up '{KEY_FILE}' securely! If lost, saved passwords cannot be recovered.{C_RESET}")
        return key
    except IOError as e:
        print(f"{C_ERROR}{E_ERROR} Could not write key file '{KEY_FILE}': {e}{C_RESET}")
        return None

def load_key():
    """Loads the Fernet key from KEY_FILE."""
    if not CRYPTOGRAPHY_AVAILABLE:
        return None
    try:
        ensure_directory_exists()
        if not os.path.exists(KEY_FILE):
            print(f"{C_INFO}{E_INFO} Encryption key file ('{KEY_FILE}') not found.{C_RESET}")
            return None
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
        if len(key) < 40:
            print(f"{C_WARNING} Key file '{KEY_FILE}' seems corrupted or too short. Please check it or delete it to generate a new one.{C_RESET}")
            return None
        return key
    except IOError as e:
        print(f"{C_ERROR}{E_ERROR} Could not read key file '{KEY_FILE}': {e}{C_RESET}")
        return None

def encrypt_password(password, key):
    """Encrypts a password using the provided key."""
    if not CRYPTOGRAPHY_AVAILABLE or not key: return password
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_password(encrypted_password, key):
    """Decrypts a password using the provided key."""
    if not CRYPTOGRAPHY_AVAILABLE or not key: return encrypted_password
    try:
        f = Fernet(key)
        decrypted_bytes = f.decrypt(encrypted_password.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"{C_ERROR}{E_ERROR} Decryption failed for a stored password! {C_RESET}")
        print(f"{C_DIM}   Error: {e}. This might happen if the key file ('{KEY_FILE}') changed or is corrupt.{C_RESET}"); return None


# === Credentials Management ===
def select_or_enter_credentials(key=None):
    """Manages credential selection/entry. Returns (username, password, was_saved)."""
    saved_creds = load_credentials()
    
    while True:
        # Display saved credentials if any exist
        if saved_creds:
            print(f"\n{C_HEADER}=== {E_SAVE} Saved Credentials ==={C_RESET}")
            [print(f"  {C_CYAN}{i}{C_RESET}. {C_BLUE}{cred['username']}{C_RESET}") for i, cred in enumerate(saved_creds, 1)]
        
        # Display options
        print(f"\n{C_HEADER}=== {E_SAVE} Options ==={C_RESET}")
        print(f"  {C_CYAN}2{C_RESET}. {C_GREEN}Add new user{C_RESET}")
        print(f"  {C_CYAN}3{C_RESET}. {C_RED}Exit{C_RESET}")
        
        choice = input(f"\n{C_PROMPT}Select an option: {C_RESET}").strip()
        
        # Handle exit
        if choice == '3':
            print(f"\n{C_INFO}{E_WAVE} Goodbye!{C_RESET}")
            sys.exit(0)
        
        # Handle new user
        if choice == '2':
            print(f"\n{C_HEADER}=== {E_SAVE} Add New User ==={C_RESET}")
            username = input(f"{C_PROMPT}Enter NIET Username: {C_CYAN}")
            print(C_RESET, end='')
            password = getpass.getpass(f"{C_PROMPT}Enter NIET Password: ")
            
            if input(f"\n{C_PROMPT}{E_SAVE} Save credentials? (y/n): {C_RESET}").strip().lower() == 'y':
                save_credentials(username, password)
            return username, password, False
        
        # Handle saved credential selection
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(saved_creds):
                return saved_creds[idx]['username'], saved_creds[idx]['password'], True
            print(f"{C_WARNING}Invalid option. Please try again.{C_RESET}")
        except ValueError:
            print(f"{C_WARNING}Invalid input. Please enter a number.{C_RESET}")

def verify_jsessionid(jsessionid):
    """Verifies if the JSESSIONID is still valid."""
    if not jsessionid:
        return False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://nietcloud.niet.co.in/studentCourseFileNew.htm?shwA=%2700A%27',
            'Cookie': f'JSESSIONID={jsessionid}'
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(
            NIET_ATTENDANCE_URL,
            params={'termId': 2, 'refreshData': 0},
            headers=headers,
            verify=False,
            timeout=10
        )
        return response.status_code == 200 and bool(response.json())
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        return False


# === Selenium Login ===
def login_and_extract_selenium(url, username, password, browser_choice=None, output_filename=SELENIUM_OUTPUT_FILE):
    """Logs in using Selenium, returns username and jsessionid if successful."""
    if not SELENIUM_AVAILABLE:
        print(f"{C_ERROR}{E_ERROR} Selenium not available. Browser login disabled.{C_RESET}")
        return None, None

    driver = None
    jsessionid = None
    if DEBUG_MODE:
        print(f"{C_INFO}{E_GEAR} Initializing browser...{C_RESET}")

    try:
        if browser_choice is None: browser_choice = get_default_browser()
        browser_name = browser_choice.capitalize()

        try: # --- WebDriver Initialization ---
            if browser_choice == 'firefox':
                options = FirefoxOptions()
                options.add_argument('--ignore-certificate-errors'); options.add_argument('--allow-running-insecure-content'); #options.add_argument('--headless') # Optional headless
                # Add preferences to potentially speed up Firefox if needed
                options.set_preference("network.http.pipelining", True)
                options.set_preference("network.http.proxy.pipelining", True)
                options.set_preference("network.http.pipelining.maxrequests", 8)
                options.set_preference("content.notify.interval", 500000)
                options.set_preference("content.notify.ontimer", True)
                options.set_preference("content.switch.threshold", 250000)
                options.set_preference("browser.cache.memory.capacity", 65536) # Increase memory cache
                options.set_preference("browser.startup.preXulSkeletonUI", False)
                options.set_preference("reader.parse-on-load.enabled", False) # Disable reader mode parsing
                options.set_preference("browser.sessionhistory.max_total_viewers", 4) # Reduce session history viewers
                options.set_preference("nglayout.initialpaint.delay", 0) # Reduce paint delay
                driver = webdriver.Firefox(options=options)
            elif browser_choice == 'edge':
                options = EdgeOptions()
                options.add_argument('--ignore-certificate-errors'); options.add_argument('--allow-running-insecure-content'); #options.add_argument('--headless') # Optional headless
                driver = webdriver.Edge(options=options)
            else: 
                if DEBUG_MODE:
                    print(f"{C_ERROR}{E_ERROR} Unsupported browser: {browser_choice}{C_RESET}")
                return None, None
        except Exception as e: 
            if DEBUG_MODE:
                print(f"{C_ERROR}{E_ERROR} Error initializing WebDriver: {e}{C_RESET}")
            return None, None

        # --- Login Steps ---
        if DEBUG_MODE:
            print(f"{C_SUCCESS}{E_COMPUTER} {browser_name} WebDriver Initialized.{C_RESET}")
            print(f"{C_INFO}{E_LOGIN} Logging into: {C_CYAN}{url}{C_RESET}")
            print(f"{C_INFO}{E_EYES} Opening page...{C_RESET}")
        driver.set_page_load_timeout(10) # Increased timeout slightly
        try: 
            driver.get(url)
            if DEBUG_MODE:
                print(f"{C_SUCCESS} Page loaded successfully{C_RESET}")
        except TimeoutException: 
            if DEBUG_MODE:
                print(f"{C_WARNING} Page load timed out, but continuing...{C_RESET}")
        except Exception as e: 
            if DEBUG_MODE:
                print(f"{C_ERROR}Error loading page: {e}{C_RESET}")
            return None, None

        if DEBUG_MODE:
            print(f"{C_INFO}Entering username...{C_RESET}")
        try:
            uname_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "j_username")))
            uname_field.clear(); uname_field.send_keys(username)
            if DEBUG_MODE:
                print(f"{C_SUCCESS} Username entered{C_RESET}")
        except Exception as e: 
            print(f"{C_ERROR}Error entering username: {e}{C_RESET}")
            return None, None

        if DEBUG_MODE:
            print(f"{C_INFO}Entering password...{C_RESET}")
        try:
            pword_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "j_password")))
            pword_field.clear(); pword_field.send_keys(password)
            if DEBUG_MODE:
                print(f"{C_SUCCESS} Password entered{C_RESET}")
        except Exception as e: 
            print(f"{C_ERROR}Error entering password: {e}{C_RESET}")
            return None, None

        if DEBUG_MODE:
            print(f"{C_INFO}Credentials entered.{C_RESET}")
        time.sleep(4) # Small delay

        try:
            login_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            if DEBUG_MODE:
                print(f"{C_INFO}{E_ROCKET} Submitting...{C_RESET}")
            login_btn.click()
            if DEBUG_MODE:
                print(f"{C_SUCCESS} Login button clicked{C_RESET}")
        except Exception as e: 
            if DEBUG_MODE:
                print(f"{C_ERROR}Error clicking login: {e}{C_RESET}")
            return None, None

        try:
            WebDriverWait(driver, 10).until(EC.any_of(
                EC.presence_of_element_located((By.ID, "logo")), EC.presence_of_element_located((By.ID, "hdWelcomeName")),
                EC.url_contains("Dashboard"), EC.presence_of_element_located((By.LINK_TEXT, "Logout")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Welcome')]"))))
            if DEBUG_MODE:
                print(f"{C_SUCCESS}{E_SUCCESS} Login successful, page loaded.{C_RESET}")
                # Correctly indented block for saving debug HTML after successful login
                try:
                    with open("after_login.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"{C_DIM}Saved debug HTML to after_login.html{C_RESET}")
                except Exception as e:
                    print(f"{C_WARNING}Could not save debug HTML: {e}{C_RESET}")
        except TimeoutException:
            if DEBUG_MODE:
                print(f"{C_WARNING}{E_WARNING} Post-login confirmation timeout. Check {output_filename}.")
                # Correctly indented block for saving debug HTML on timeout
                try:
                    with open("login_timeout.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"{C_DIM}Saved debug HTML to login_timeout.html{C_RESET}")
                except Exception as e:
                    print(f"{C_WARNING}Could not save debug HTML: {e}{C_RESET}")
        except WebDriverException as e: 
            if DEBUG_MODE:
                print(f"{C_ERROR}{E_ERROR} Error waiting for login confirmation: {e}{C_RESET}")

        # Save main output HTML regardless of confirmation success
        try: 
            pg_src = driver.page_source
        except Exception as e: 
            pg_src = f"Error getting page source: {e}"
            if DEBUG_MODE:
                print(f"{C_ERROR}Could not get page source: {e}{C_RESET}")
        # Correctly indented block for saving main HTML output
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                 f.write(pg_src)
            if DEBUG_MODE:
                print(f"{C_DIM}HTML saved to {output_filename}{C_RESET}")
        except IOError as e:
            if DEBUG_MODE:
                print(f"{C_WARNING}Could not save HTML output: {e}{C_RESET}")

        cookies = driver.get_cookies()
        jsessionid = next((c['value'] for c in cookies if c['name'] == 'JSESSIONID'), None)

        if jsessionid: 
            if DEBUG_MODE:
                print(f"{C_SUCCESS}{E_SUCCESS} JSESSIONID obtained.{C_RESET}")
        else: 
            print(f"{C_ERROR}{E_ERROR} JSESSIONID NOT found. Login likely FAILED. Check {output_filename} and debug HTML files.{C_RESET}")
            return None, None

    except (TimeoutException, WebDriverException, Exception) as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Selenium Error ({browser_name}): {e}{C_RESET}")
            print(f"{C_DIM}{traceback.format_exc()}{C_RESET}")
        jsessionid = None
    finally:
        if driver: 
            if DEBUG_MODE:
                print(f"{C_INFO}{E_LOGOUT} Closing browser...{C_RESET}")
            driver.quit()
        else: # Ensure stop if driver init failed
            if _loading_thread and _loading_thread.is_alive(): 
                stop_loading()

    # Return the original username passed in, assuming login success implies it's correct
    return username if jsessionid else None, jsessionid


# === Attendance Data Fetching ===
def toggle_debug_mode():
    """Toggle debug mode on/off"""
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    print(f"{C_INFO}{E_GEAR} Debug mode {'enabled' if DEBUG_MODE else 'disabled'}.{C_RESET}")

def fetch_attendance_data(jsessionid, bypass_ssl_verify=False):
    """Fetches attendance data using JSESSIONID. Can bypass SSL verification."""
    if not jsessionid: 
        print(f"{C_ERROR}{E_ERROR} No JSESSIONID provided.{C_RESET}")
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd', 'X-Requested-With': 'XMLHttpRequest', 'Connection': 'keep-alive',
        'Referer': 'https://nietcloud.niet.co.in/studentCourseFileNew.htm?shwA=%2700A%27', 'Cookie': f'JSESSIONID={jsessionid}'
    }
    params = {'termId': 2, 'refreshData': 0}
    url = NIET_ATTENDANCE_URL

    if DEBUG_MODE:
        print(f"{C_INFO}{E_ROCKET} Fetching attendance data...{C_RESET}")
        start_loading("Requesting from NIET Cloud...")
    data = None; raw_text = ""; response = None

    verify_ssl = True
    if bypass_ssl_verify:
        if DEBUG_MODE:
            print(f"{C_WARNING}{E_WARNING} Bypassing SSL certificate verification.{C_RESET}")
        try: urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except AttributeError: 
            if DEBUG_MODE:
                print(f"{C_WARNING}Could not disable urllib3 InsecureRequestWarning.{C_RESET}")
        verify_ssl = False

    try:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)

        response = session.get(url, params=params, headers=headers, verify=verify_ssl, timeout=30)
        if DEBUG_MODE:
            stop_loading()

        try: raw_text = response.content.decode('utf-8', errors='replace')
        except Exception: raw_text = str(response.content) # Fallback
        content_type = response.headers.get('Content-Type', '').lower()

        if DEBUG_MODE: # Print debug info if enabled
            print(f"\n{C_DIM}--- Request Debug Info ---")
            print(f"URL: {response.url}\nStatus Code: {response.status_code}\nContent-Type: {content_type}")
            print(f"--- Response Body (First 500 chars) ---\n{C_YELLOW}{raw_text[:500]}{C_RESET}\n--- End Debug Info ---{C_RESET}")

        response.raise_for_status() # Check for HTTP errors AFTER getting potential content

        if 'application/json' not in content_type:
            if DEBUG_MODE:
                print(f"{C_ERROR}{E_ERROR} Server didn't return JSON (Content-Type: '{content_type}'). Cannot parse.{C_RESET}")
                try: # Correctly indented block for saving non-JSON
                    with open("non_json_response.txt", "w", encoding="utf-8") as f: f.write(raw_text)
                    print(f"{C_INFO}Unexpected response saved to non_json_response.txt{C_RESET}")
                except Exception as save_err: print(f"{C_WARNING}Could not save non-JSON response: {save_err}{C_RESET}")
            return None

        data = response.json()

        try: # Save fetched data
            with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
            if DEBUG_MODE:
                print(f"{C_SUCCESS}{E_SUCCESS} Fresh data saved to '{ATTENDANCE_FILE}'.{C_RESET}")
        except (IOError, TypeError) as e:
            if DEBUG_MODE:
                print(f"{C_WARNING}{E_WARNING} Could not save fetched data to {ATTENDANCE_FILE}: {e}{C_RESET}")

    except requests.exceptions.Timeout:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Request timed out.{C_RESET}")
    except requests.exceptions.SSLError as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} SSL Error: {e}.{C_YELLOW} Try again or check certs.{C_RESET}")
    except requests.exceptions.ConnectionError as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Connection Error: {e}.{C_INFO} Check network/firewall.{C_RESET}")
    except requests.exceptions.HTTPError as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} HTTP Error: {e}. {C_YELLOW} Check JSESSIONID validity.{C_RESET}" if response and response.status_code in [401, 403] else "")
    except requests.exceptions.RequestException as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Network Error: {e}{C_RESET}")
    except json.JSONDecodeError as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Failed to decode JSON response: {e}{C_RESET}")
            if DEBUG_MODE: print(f"{C_INFO}Check the 'Response Body' printed above.{C_RESET}")
            else: print(f"{C_INFO}Response was not valid JSON. Server might be returning an error page.{C_RESET}")
            if raw_text:
                try:
                    with open("json_decode_error_response.txt", "w", encoding="utf-8") as f:
                        f.write(raw_text)
                    print(f"{C_INFO}Problematic response saved to json_decode_error_response.txt{C_RESET}")
                except Exception as save_err:
                    print(f"{C_WARNING}Could not save error response: {save_err}{C_RESET}")
    except Exception as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Unexpected error during fetch: {e}\n{C_DIM}{traceback.format_exc()}{C_RESET}")
    finally:
        if _loading_thread and _loading_thread.is_alive(): stop_loading()
    return data


# === Data Loading / Processing / Display ===
def load_attendance_data(json_file=ATTENDANCE_FILE):
    """Loads attendance data from a JSON file."""
    try:
        with open(json_file,'r', encoding='utf-8') as f: print(f"{C_INFO}{E_INFO} Loading data from '{C_CYAN}{json_file}{C_INFO}'...{C_RESET}"); return json.load(f)
    except FileNotFoundError: print(f"{C_ERROR}{E_ERROR} File not found: '{json_file}'.{C_RESET}"); return None
    except json.JSONDecodeError: print(f"{C_ERROR}{E_ERROR} Invalid JSON in '{json_file}'.{C_RESET}"); return None
    except Exception as e: print(f"{C_ERROR}{E_ERROR} Error loading {json_file}: {e}{C_RESET}"); return None

def extract_summary_data(data):
    """Extracts and formats summary attendance data for display, preparing for rich."""
    if not isinstance(data, list): print(f"{C_ERROR}{E_ERROR} Invalid data format.{C_RESET}"); return [], 0, 0
    summary=[]; total_p=0; total_c=0
    for sub in data:
        if not isinstance(sub, dict): print(f"{C_WARNING}{E_WARNING} Skipping invalid entry: {sub}{C_RESET}"); continue
        try:
            p=int(sub.get('presentCount',0)); a=int(sub.get('absentCount',0)); t=p+a
            perc=(p/t*100)if t>0 else 0.0
            perc_s=f"{perc:.2f}%"
            emoji = ""; rich_style = "" # Rich style string
            if t > 0:
                if perc < 75: rich_style, emoji = "bold red", E_SAD
                elif perc < 85: rich_style, emoji = "bold yellow", E_NEUTRAL
                else: rich_style, emoji = "bold green", E_HAPPY
            else: rich_style, emoji = "dim", " " # Dim for N/A, space for alignment
            subj_name = sub.get('subject', 'N/A'); subj_code = sub.get('subjectCode', 'N/A')
            summary.append({
                'Code': f"{subj_code}", f'{E_BOOK} Course': f"{subj_name}", 'Count': f"{p}/{t}",
                f'{E_CHART_UP} %': perc_s, ' ': emoji, '_style': rich_style })
            total_p+=p; total_c+=t
        except (ValueError, TypeError) as e: print(f"{C_WARNING}{E_WARNING} Error processing subject ({sub.get('subjectCode','N/A')}): {e}. Skipping.{C_RESET}"); continue
    ov_perc=(total_p/total_c*100)if total_c>0 else 0.0
    ov_emoji = ""; ov_rich_style = ""
    if total_c > 0:
        if ov_perc < 75: ov_rich_style, ov_emoji = "bold red", E_SAD
        elif ov_perc < 85: ov_rich_style, ov_emoji = "bold yellow", E_NEUTRAL
        else: ov_rich_style, ov_emoji = "bold green", E_HAPPY
    else: ov_rich_style, ov_emoji = "dim", " "
    ov_perc_s = f"{ov_perc:.2f}%"
    summary.append({
        'Code': '', f'{E_BOOK} Course': 'TOTAL', 'Count': f"{total_p}/{total_c}",
        f'{E_CHART_UP} %': ov_perc_s, ' ': ov_emoji, '_style': "bold white" })
    return summary,total_p,total_c

def extract_detailed_attendance(sub_data):
    """Extracts and formats detailed attendance, preparing for rich."""
    details=[]; p_entries=[]
    att_str = sub_data.get('studentAttendanceData','');
    if not att_str: return details
    for entry in att_str.split(';'):
        if not entry: continue
        parts=entry.split('^^^');
        if len(parts)>=6:
            d_s,s_t,e_t,st,sess,_=parts[:6]
            try:
                d_o=datetime.strptime(d_s.strip(),'%b %d, %Y'); st_l=st.lower().strip()
                status_text = ""; status_emoji = ""; rich_style = ""
                if st_l=='present': status_text, status_emoji, rich_style = "Present", E_PRESENT, "green"
                elif st_l=='absent': status_text, status_emoji, rich_style = "Absent", E_ABSENT, "red"
                else: status_text, status_emoji, rich_style = st, E_OTHER_STATUS, "yellow"
                p_entries.append({
                    'd_o': d_o, 'Sr': 0, f'{E_CALENDAR} Date': d_o.strftime('%b %d, %Y'), f'{E_CLOCK} Time': f"{s_t}-{e_t}",
                    'Session': sess, 'Status': status_text, ' ': status_emoji, '_style': rich_style })
            except ValueError: print(f"{C_WARNING}Date parse error: {entry}{C_RESET}"); continue
        else: print(f"{C_WARNING}Malformed entry: {entry}{C_RESET}")
    p_entries.sort(key=lambda x:x['d_o'],reverse=True)
    for i,item in enumerate(p_entries,1): item['Sr']=f"{i}"; del item['d_o']; details.append(item)
    return details

# --- REWRITTEN: display_summary (using rich with lines) ---
def display_summary(summary_data):
    """Displays the attendance summary table using rich if available."""
    if not summary_data: print(f"{C_WARNING}{E_WARNING} No summary data.{C_RESET}"); return

    if RICH_AVAILABLE:
        console = Console()
        data_rows = summary_data[:-1]
        total_row_dict = summary_data[-1]
        if not data_rows and not total_row_dict: print(f"{C_WARNING}No data found.{C_RESET}"); return

        headers = list(summary_data[0].keys()) if summary_data else []
        headers = [h for h in headers if not h.startswith('_')] # Remove internal keys

        table = Table(show_header=True, header_style="bold cyan", border_style="dim", show_edge=True, box=box.SQUARE, show_lines=True) # Added show_lines=True
        table.add_column(headers[0], style="dim", justify="left", min_width=15) # Code
        table.add_column(headers[1], justify="left", min_width=40) # Course Name
        table.add_column(headers[2], justify="center") # Count
        table.add_column(headers[3], justify="right") # %
        table.add_column(headers[4], justify="center", no_wrap=True) # Emoji

        for row_dict in data_rows:
            row_values = [row_dict.get(h, '') for h in headers]
            row_style = row_dict.get('_style', "")
            row_values[3] = f"[{row_style}]{row_values[3]}[/]" # Style percentage
            row_values[0] = f"[dim]{row_values[0]}[/]" # Style code dim
            row_values[1] = f"[magenta]{row_values[1]}[/]" # Style course name
            table.add_row(*row_values)

        total_values = [total_row_dict.get(h, '') for h in headers]
        total_style = total_row_dict.get('_style', "bold white") # Get TOTAL row style
        table.add_row(*total_values, style=total_style) # Style the whole TOTAL row

        print(f"\n{C_HEADER}{E_STAR}=== Attendance Summary ==={E_STAR}{C_RESET}\n")
        console.print(table)

    elif TABULATE_AVAILABLE: # Fallback to tabulate
        tabulate_data = []
        for row_dict in summary_data:
            perc_s = row_dict[f'{E_CHART_UP} %']
            style = row_dict['_style']; color_c = ""
            if style == "bold red": color_c = C_LOW + C_BOLD
            elif style == "bold yellow": color_c = C_MID + C_BOLD
            elif style == "bold green": color_c = C_HIGH + C_BOLD
            elif style == "dim": color_c = C_DIM
            elif style == "bold white": color_c = C_WHITE + C_BOLD
            if row_dict[f'{E_BOOK} Course'] == 'TOTAL':
                 tab_row = { 'Code': f"{color_c}{row_dict['Code']}{C_RESET}", f'{E_BOOK} Course': f"{color_c}{row_dict[f'{E_BOOK} Course']}{C_RESET}", 'Count': f"{color_c}{row_dict['Count']}{C_RESET}", f'{E_CHART_UP} %': f"{color_c}{perc_s}{C_RESET}", ' ': f"{color_c}{row_dict[' ']}{C_RESET}" }
            else: tab_row = { 'Code': f"{C_DIM}{row_dict['Code']}{C_RESET}", f'{E_BOOK} Course': f"{C_SUBJECT}{row_dict[f'{E_BOOK} Course']}{C_RESET}", 'Count': row_dict['Count'], f'{E_CHART_UP} %': f"{color_c}{perc_s}{C_RESET}" if color_c else perc_s, ' ': row_dict[' '] }
            tabulate_data.append(tab_row)
        try: df=pd.DataFrame(tabulate_data); print(f"\n{C_HEADER}{E_STAR}=== Attendance Summary ==={E_STAR}{C_RESET}\n"); print(tabulate(df,headers='keys',tablefmt='fancy_grid',showindex=False)) # Use fancy_grid for lines
        except Exception as e: print(f"{C_ERROR}{E_ERROR} Tabulate error: {e}\n{C_DIM}Data: {summary_data}{C_RESET}")
    else: # Basic fallback
        print(f"\n{C_HEADER}{E_STAR}=== Attendance Summary ==={E_STAR}{C_RESET}\n")
        headers = list(summary_data[0].keys()) if summary_data else []
        headers = [h for h in headers if not h.startswith('_')]
        if headers: print(" | ".join(headers))
        for row_dict in summary_data: print(" | ".join(str(row_dict.get(h, '')) for h in headers))


# --- REWRITTEN: display_subject_details (using rich with lines) ---
def display_subject_details(subject, details_data):
    """Displays the detailed attendance table for a subject using rich if available."""
    if not details_data: print(f"\n{C_WARNING}{E_WARNING} No details for {C_SUBJECT}{subject}{C_RESET}.{C_RESET}"); return

    if RICH_AVAILABLE:
        console = Console()
        headers = list(details_data[0].keys()) if details_data else []
        headers = [h for h in headers if not h.startswith('_')]

        table = Table(title=f"Details: [bold magenta]{subject}[/]", show_header=True, header_style="bold cyan", border_style="dim", show_edge=True, box=box.SQUARE, show_lines=True) # Added show_lines=True
        table.add_column(headers[0], style="dim", justify="right") # Sr
        table.add_column(headers[1], justify="left")  # Date
        table.add_column(headers[2], justify="center") # Time
        table.add_column(headers[3], justify="left")  # Session
        table.add_column(headers[4], justify="left")  # Status Text
        table.add_column(headers[5], justify="center", no_wrap=True) # Emoji

        for row_dict in details_data:
            row_values = [row_dict.get(h, '') for h in headers]
            row_style = row_dict.get('_style', "") # Style for status
            row_values[4] = f"[{row_style}]{row_values[4]}[/]" # Style the status text
            row_values[0] = f"[dim]{row_values[0]}[/]" # Dim Sr
            table.add_row(*row_values)

        print("") # Add a newline before the table
        console.print(table)

    elif TABULATE_AVAILABLE: # Fallback to tabulate
        tabulate_data = []
        for row_dict in details_data:
            status_text = row_dict['Status']; style = row_dict['_style']; color_c = ""
            if style == "green": color_c = C_GREEN
            elif style == "red": color_c = C_RED
            elif style == "yellow": color_c = C_YELLOW
            tab_row = { 'Sr': f"{C_DIM}{row_dict['Sr']}{C_RESET}", f'{E_CALENDAR} Date': row_dict[f'{E_CALENDAR} Date'], f'{E_CLOCK} Time': row_dict[f'{E_CLOCK} Time'], 'Session': row_dict['Session'], 'Status': f"{color_c}{status_text}{C_RESET}" if color_c else status_text, ' ': row_dict[' '] }
            tabulate_data.append(tab_row)
        try: df=pd.DataFrame(tabulate_data); subj_d=f"{C_SUBJECT}{C_BOLD}{subject}{C_RESET}"; print(f"\n{C_HEADER}=== {E_EYES} Details: {subj_d} ==={C_RESET}\n"); print(tabulate(df,headers='keys',tablefmt='fancy_grid',showindex=False)) # Use fancy_grid for lines
        except Exception as e: print(f"{C_ERROR}{E_ERROR} Tabulate error: {e}\n{C_DIM}Data: {details_data}{C_RESET}")
    else: # Basic fallback
        subj_d=f"{C_SUBJECT}{C_BOLD}{subject}{C_RESET}"; print(f"\n{C_HEADER}=== {E_EYES} Details: {subj_d} ==={C_RESET}\n")
        headers = list(details_data[0].keys()) if details_data else []; headers = [h for h in headers if not h.startswith('_')]
        if headers: print(" | ".join(headers))
        for row_dict in details_data: print(" | ".join(str(row_dict.get(h, '')) for h in headers))


# === Calculations ===
# Use lowercase list/tuple hints (Requires Python 3.9+)
def generate_future_schedule(days_ahead: int, holidays: set = None) -> list[tuple[date, int]]:
    """Generates a schedule for future days, excluding today."""
    if holidays is None: holidays = set()
    schedule = []
    curr_d = date.today()
    classes_per_weekday = {0: 7, 1: 7, 2: 7, 3: 7, 4: 7, 5: 6, 6: 0} # Mon-Sun
    for i in range(1, days_ahead + 1):
        temp_d = curr_d + timedelta(days=i)
        date_str = temp_d.strftime("%Y-%m-%d"); is_holiday = date_str in holidays
        dow = temp_d.weekday(); cls_day = 0
        if not is_holiday: cls_day = classes_per_weekday.get(dow, 0)
        schedule.append((temp_d, cls_day))
    return schedule

# Use lowercase list/tuple hints (Requires Python 3.9+)
def calculate_classes_needed_for_target(total_present: int, total_classes: int, future_schedule: list[tuple[date, int]], target_percentage: float = 85.0) -> tuple[int, int, float]:
    """Calculates classes needed to reach target % considering future schedule."""
    if target_percentage > 100: target_percentage = 100
    if target_percentage <= 0: return 0, 0, (total_present / total_classes * 100) if total_classes > 0 else 0.0
    curr_p = (total_present / total_classes * 100) if total_classes > 0 else 0.0
    if curr_p >= target_percentage: return 0, 0, curr_p
    numerator = (target_percentage * total_classes - 100 * total_present)
    denominator = (100 - target_percentage)
    if denominator <= 1e-9: return float('inf'), float('inf'), curr_p
    if numerator <= 0: classes_needed_raw = 1 # Need at least 1 if below target and formula negative/zero
    else: classes_needed_raw = math.ceil(numerator / denominator)
    classes_accumulated = 0; unique_days_needed = set(); possible_to_reach = False
    for day_date, classes_on_day in future_schedule:
        if classes_on_day > 0:
            can_attend_today = min(classes_on_day, classes_needed_raw - classes_accumulated)
            if can_attend_today > 0:
                classes_accumulated += can_attend_today; unique_days_needed.add(day_date)
                if classes_accumulated >= classes_needed_raw: possible_to_reach = True; break
    if not possible_to_reach: return float('inf'), float('inf'), curr_p
    total_future_classes_in_schedule = sum(classes for _, classes in future_schedule)
    projected_total_present = total_present + classes_needed_raw
    projected_total_classes = total_classes + total_future_classes_in_schedule
    projected_percentage = (projected_total_present / projected_total_classes * 100) if projected_total_classes > 0 else 0.0
    return int(classes_needed_raw), len(unique_days_needed), projected_percentage

# Use lowercase list/dict hints (Requires Python 3.9+)
def calculate_leave_allowance(total_present: int, total_classes: int, future_schedule: list[tuple[date, int]], target_percentage: float = 85.0) -> dict[str, any]:
    """Calculates max allowed absences based on current state and estimates future days."""
    if target_percentage > 100: target_percentage = 100
    if target_percentage <= 0: target_percentage = 0.1
    curr_p = (total_present / total_classes * 100) if total_classes > 0 else 0.0
    max_abs = 0; can_m = False
    if curr_p >= target_percentage:
        if target_percentage > 0: max_abs = math.floor((total_present * 100 / target_percentage) - total_classes)
        else: max_abs = float('inf')
        if max_abs < 0: max_abs = 0
        can_m = True
    abs_remaining = max_abs; unique_leave_days = set()
    estimated_days = 0
    if can_m and max_abs > 0 and max_abs != float('inf'):
        for day_date, classes_on_day in future_schedule:
            if abs_remaining <= 0: break
            if classes_on_day > 0:
                absences_today = min(classes_on_day, abs_remaining)
                if absences_today > 0: abs_remaining -= absences_today; unique_leave_days.add(day_date)
        estimated_days = len(unique_leave_days)
    elif max_abs == float('inf'): estimated_days = float('inf')
    return {'current_percentage': curr_p, 'target_percentage': target_percentage, 'max_absences': int(max_abs) if max_abs != float('inf') else float('inf'), 'estimated_days_leave': estimated_days, 'can_maintain_target': can_m}

def calculate_future_attendance(total_present, total_classes, end_date_str, holidays=None):
    """Calculates projected attendance based on various future attendance rates."""
    holidays_set = set(holidays) if holidays else set()
    try:
        end_d = datetime.strptime(end_date_str, "%Y-%m-%d").date(); curr_d = date.today()
        if curr_d >= end_d: return {'error': 'End date must be in the future.'}
        future_classes_total = 0; future_days_schedule = []; temp_d = curr_d
        classes_per_weekday = {0: 7, 1: 7, 2: 7, 3: 7, 4: 7, 5: 6, 6: 0} # Mon-Sun
        while temp_d <= end_d:
            date_str = temp_d.strftime("%Y-%m-%d"); is_holiday = date_str in holidays_set
            dow = temp_d.weekday(); cls_day = 0
            if not is_holiday: cls_day = classes_per_weekday.get(dow, 0)
            if temp_d > curr_d:
                 future_days_schedule.append((temp_d, cls_day))
                 if cls_day > 0: future_classes_total += cls_day
            temp_d += timedelta(days=1)
        projected_total_classes = total_classes + future_classes_total
        curr_p = (total_present / total_classes * 100) if total_classes > 0 else 0.0
        classes_needed_for_85, _, _ = calculate_classes_needed_for_target(total_present, total_classes, future_days_schedule, 85.0)
        scenarios = []; percentages_to_check = [100, 95, 90, 85, 75, 50, 0]
        for future_attend_percent in percentages_to_check:
            future_present_count = 0; days_required_for_classes = 0
            if future_classes_total > 0:
                future_present_count = math.floor(future_classes_total * (future_attend_percent / 100.0))
                classes_to_attend_counter = future_present_count; unique_days_to_attend = set()
                for day_date, classes_on_day in future_days_schedule:
                    if classes_to_attend_counter <= 0: break
                    if classes_on_day > 0:
                        attended_today = min(classes_on_day, classes_to_attend_counter)
                        if attended_today > 0: unique_days_to_attend.add(day_date); classes_to_attend_counter -= attended_today
                days_required_for_classes = len(unique_days_to_attend)
            projected_total_present = total_present + future_present_count
            projected_percentage = (projected_total_present / projected_total_classes * 100) if projected_total_classes > 0 else 0.0
            scenarios.append({'future_attendance': future_attend_percent, 'classes_to_attend': future_present_count, 'days_to_attend': days_required_for_classes, 'projected_total': f"{projected_total_present}/{projected_total_classes}", 'projected_percentage': round(projected_percentage, 2)})
        return {'current_total': f"{total_present}/{total_classes}", 'current_percentage': round(curr_p, 2), 'future_classes': future_classes_total, 'future_total_classes': projected_total_classes, 'classes_needed_85': classes_needed_for_85, 'scenarios': scenarios}
    except ValueError: return {'error': 'Invalid date format. Please use YYYY-MM-DD.'}
    except Exception as e: print(f"{C_ERROR}Future calc error: {e}\n{C_DIM}{traceback.format_exc()}{C_RESET}"); return {'error': 'Unexpected error.'}


# === Calculation Display ===
# Use lowercase dict/list/tuple hints (Requires Python 3.9+)
def display_leave_allowance_results(result: dict[str, any], total_p: int, total_c: int, future_schedule: list[tuple[date, int]], target_percentage: float):
    """Displays the results of the leave allowance calculation."""
    print(f"\n{C_HEADER}{E_TARGET}=== Leave Allowance Calculator (Target: {target_percentage}%) ==={C_RESET}\n")
    print(f"Current Attendance: {result['current_percentage']:.2f}% ({total_p}/{total_c})")
    if result['can_maintain_target']:
        if result['max_absences'] == float('inf'): print(f"\n{C_GREEN}{E_HAPPY} Can miss unlimited classes.{C_RESET}")
        elif result['max_absences'] == 0: print(f"\n{C_YELLOW}{E_NEUTRAL} At target, but cannot miss more classes ({C_BOLD}0{C_RESET}{C_YELLOW} max absences) to stay >= {target_percentage}%.{C_RESET}")
        else:
            print(f"\n{C_GREEN}{E_HAPPY} Can miss up to {C_BOLD}{result['max_absences']}{C_RESET}{C_GREEN} classes and stay >= {target_percentage}%.{C_RESET}")
            est_days = result['estimated_days_leave']
            if est_days == float('inf'): print(f"{C_GREEN}   Corresponds to unlimited leave days.{C_RESET}")
            elif est_days is not None: print(f"{C_GREEN}   Based on schedule, approx. {C_BOLD}{est_days}{C_RESET}{C_GREEN} unique leave days.{C_RESET}")
    else: # Below target
        print(f"\n{C_WARNING}{E_SAD} Currently below {target_percentage:.2f}% target.{C_RESET}")
        cls_n, days_n, _ = calculate_classes_needed_for_target(total_p, total_c, future_schedule, target_percentage) # Use the passed schedule
        if cls_n == float('inf'): print(f"{C_ERROR}{E_ERROR} Impossible to reach {target_percentage:.2f}% based on schedule.{C_RESET}")
        elif cls_n > 0:
            print(f"{C_YELLOW}{E_POINT_RIGHT} Need to attend next {C_BOLD}{cls_n}{C_RESET}{C_YELLOW} classes consecutively.{C_RESET}")
            if days_n != float('inf'): print(f"{C_YELLOW}   Approx. {C_BOLD}{days_n}{C_RESET}{C_YELLOW} unique future school days (within schedule).{C_RESET}")
            immediate_new_p = (total_p + cls_n) / (total_c + cls_n) * 100 if (total_c + cls_n) > 0 else 0
            print(f"{C_YELLOW}   Immediately after, attendance would be ~{C_BOLD}{immediate_new_p:.2f}%{C_RESET}{C_YELLOW}.{C_RESET}")
        else: print(f"{C_YELLOW}{E_THINK} No classes needed, but below target? Check logic.{C_RESET}")

# --- REWRITTEN: display_future_attendance_results (using rich with lines) ---
def display_future_attendance_results(result):
    """Displays the results of the future attendance projection using rich if available."""
    if 'error' in result: print(f"\n{C_ERROR}{E_ERROR} {result['error']}{C_RESET}"); return

    print(f"\n{C_HEADER}{E_CALENDAR}=== Future Attendance Projection ==={C_RESET}\n")
    print(f"Current Attendance: {result['current_total']} ({result['current_percentage']}%)")
    print(f"Total Future Classes Until End Date: {result['future_classes']}")
    print(f"Projected Total Classes by End Date: {result['future_total_classes']}")

    if result['classes_needed_85'] != 0:
        if result['classes_needed_85'] == float('inf'): print(f"\n{C_ERROR}{E_CHART_DOWN} Impossible to reach 85% overall by end date based on schedule.{C_RESET}")
        elif result['classes_needed_85'] > 0: print(f"\n{C_YELLOW}{E_TARGET} To reach 85% overall, must attend >= {C_BOLD}{result['classes_needed_85']}{C_RESET}{C_YELLOW} of the {result['future_classes']} future classes.{C_RESET}")
    else: print(f"\n{C_GREEN}{E_HAPPY} Projected to be >= 85% by end date if attending all future classes.{C_RESET}")

    print(f"\n{C_BLUE}{E_THINK} Projections based on different future attendance rates:{C_RESET}")
    scen_data = [] # Prepare data for display
    for s in result['scenarios']:
         proj_p = s['projected_percentage']
         emoji = ""; rich_style = ""
         if result['projected_total_classes'] > 0:
             if proj_p < 75: rich_style, emoji = "bold red", E_SAD
             elif proj_p < 85: rich_style, emoji = "bold yellow", E_NEUTRAL
             else: rich_style, emoji = "bold green", E_HAPPY
         else: rich_style, emoji = "dim", " "
         scen_data.append({
             f'{E_ROCKET}Future %': f"{s['future_attendance']}%", 'Classes Attended': str(s['classes_to_attend']), 'Est. Unique Days': str(s['days_to_attend']),
             'Proj. Total': s['projected_total'], f'{E_CHART_UP}Proj. %': f"{proj_p:.2f}%", ' ': emoji, '_style': rich_style })

    if RICH_AVAILABLE:
        console = Console()
        headers = [h for h in scen_data[0].keys() if not h.startswith('_')] if scen_data else []
        table = Table(show_header=True, header_style="bold cyan", border_style="dim", show_edge=True, box=box.SQUARE, show_lines=True) # Added show_lines=True
        table.add_column(headers[0], justify="right"); table.add_column(headers[1], justify="right"); table.add_column(headers[2], justify="right")
        table.add_column(headers[3], justify="center"); table.add_column(headers[4], justify="right"); table.add_column(headers[5], justify="center", no_wrap=True)
        for row_dict in scen_data:
            row_values = [row_dict.get(h, '') for h in headers]
            row_style = row_dict.get('_style', "")
            table.add_row(*row_values, style=row_style) # Style the whole row based on projected %
        console.print(table)

    elif TABULATE_AVAILABLE: # Fallback to tabulate
        tabulate_data = []
        for row_dict in scen_data:
            perc_s = row_dict[f'{E_CHART_UP}Proj. %']; style = row_dict['_style']; color_c = ""
            if style == "bold red": color_c = C_LOW + C_BOLD
            elif style == "bold yellow": color_c = C_MID + C_BOLD
            elif style == "bold green": color_c = C_HIGH + C_BOLD
            elif style == "dim": color_c = C_DIM
            tab_row = { h: row_dict[h] for h in row_dict if not h.startswith('_') }
            tab_row[f'{E_CHART_UP}Proj. %'] = f"{color_c}{perc_s}{C_RESET}" if color_c else perc_s
            tabulate_data.append(tab_row)
        try: df = pd.DataFrame(tabulate_data); print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False)) # Use fancy_grid for lines
        except Exception as e: print(f"{C_ERROR}{E_ERROR} Tabulate error: {e}\n{C_DIM}Data: {scen_data}{C_RESET}")
    else: # Basic fallback
         headers = [h for h in scen_data[0].keys() if not h.startswith('_')] if scen_data else []
         if headers: print(" | ".join(headers))
         for row_dict in scen_data: print(" | ".join(str(row_dict.get(h, '')) for h in headers))


# === Main Loop ===
def run_attendance_tracker(attendance_data):
    """Main interactive loop for displaying data and calculations."""
    if not attendance_data: print(f"{C_WARNING}{E_WARNING} No attendance data.{C_RESET}"); return
    summary, total_p, total_c = extract_summary_data(attendance_data)
    if not summary: print(f"{C_ERROR}{E_ERROR} Failed to extract summary.{C_RESET}"); return

    default_future_days = 90; default_holidays = set()
    try:
        default_schedule = generate_future_schedule(default_future_days, default_holidays)
        if DEBUG_MODE:
            print(f"\n{C_DIM}(Using {default_future_days}-day future schedule for calculations. Holidays: {len(default_holidays)}){C_RESET}")
    except Exception as e: print(f"{C_ERROR}Failed to generate schedule: {e}{C_RESET}"); default_schedule = []

    display_summary(summary) # Initial display

    if total_c > 0: # Initial Alert Check
        curr_p = (total_p / total_c * 100); target_alert = 85.0
        if curr_p < target_alert:
            cls_n, days_n, _ = calculate_classes_needed_for_target(total_p, total_c, default_schedule, target_alert)
            alert_border = f"{C_RED}{'='*20} {E_WARNING} ALERT {E_WARNING} {'='*20}{C_RESET}"; print("\n" + alert_border)
            print(f"{C_WARNING}Overall attendance ({C_BOLD}{curr_p:.2f}%{C_RESET}{C_WARNING}) is below {target_alert}%! {E_SAD}{C_RESET}")
            if cls_n == float('inf'): print(f"{C_ERROR}{E_ERROR} Impossible to reach {target_alert}% based on default schedule.{C_RESET}")
            elif cls_n > 0:
                print(f"{C_YELLOW}{E_POINT_RIGHT} Need to attend next {C_BOLD}{cls_n}{C_RESET}{C_YELLOW} classes consecutively.{C_RESET}")
                if days_n != float('inf'): print(f"{C_YELLOW}   Approx. {C_BOLD}{days_n}{C_RESET}{C_YELLOW} unique future school days (next {default_future_days} days).{C_RESET}")
            plain_border_len = len(f"{'='*20}  ALERT  {'='*20}"); print(f"{C_RED}{'=' * plain_border_len}{C_RESET}")

    while True:
        print(f"\n{C_HEADER}--- {E_GEAR} Options Menu ---{C_RESET}")
        print(f"  {C_CYAN}1{C_RESET}. {E_EYES} View Detailed Attendance (Subject)")
        print(f"  {C_CYAN}2{C_RESET}. {E_TARGET} Calculate Leave Allowance (>= 85%, {default_future_days}-day schedule)")
        print(f"  {C_CYAN}3{C_RESET}. {E_CALENDAR} Project Future Attendance (Custom End Date)")
        print(f"  {C_CYAN}4{C_RESET}. {E_CHART_UP} Calculate Classes Needed (Custom Target %, {default_future_days}-day schedule)")
        print(f"  {C_CYAN}5{C_RESET}. {E_BOOK} View Overall Summary Again")
        print(f"  {C_CYAN}6{C_RESET}. {E_GEAR} Toggle Debug Mode ({C_GREEN if DEBUG_MODE else C_RED}{'ON' if DEBUG_MODE else 'OFF'}{C_RESET})") # Added debug toggle option
        print(f"  {C_CYAN}0{C_RESET}. {E_LOGOUT} Exit")
        try:
            choice = int(input(f"\n{C_PROMPT}Enter choice: {C_RESET}").strip())
            print("-" * 40)
            if choice == 0: print(f"{C_INFO}{E_WAVE} Exiting tracker menu.{C_RESET}"); break
            elif choice == 1:
                 subject_map = {}; print(f"{C_BLUE}{E_BOOK} Select Subject:{C_RESET}")
                 valid_subjects = [sub for sub in attendance_data if isinstance(sub, dict) and sub.get('subjectCode')]
                 if not valid_subjects: print(f"{C_WARNING}No valid subjects found.{C_RESET}"); continue
                 for i, sub in enumerate(valid_subjects):
                     display_index = i + 1; subject_map[display_index] = sub
                     print(f"  {C_CYAN}{display_index}{C_RESET}. {sub.get('subject', 'N/A')} [{C_DIM}{sub.get('subjectCode', 'N/A')}{C_RESET}]")
                 if not subject_map: print(f"{C_WARNING}No subjects to display.{C_RESET}"); continue
                 try:
                     sub_choice = int(input(f"\n{C_PROMPT}Enter subject number: {C_RESET}").strip())
                     if sub_choice in subject_map:
                         selected_subject_data = subject_map[sub_choice]
                         details = extract_detailed_attendance(selected_subject_data)
                         display_subject_details(selected_subject_data.get('subject', 'N/A'), details)
                     else: print(f"{C_WARNING}Invalid subject number.{C_RESET}")
                 except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
            elif choice == 2:
                 target_leave = 85.0; result = calculate_leave_allowance(total_p, total_c, default_schedule, target_leave)
                 display_leave_allowance_results(result, total_p, total_c, default_schedule, target_leave) # Pass schedule here
            elif choice == 3:
                while True:
                     end_date_str = input(f"{C_PROMPT}{E_CALENDAR} Enter end date (YYYY-MM-DD): {C_RESET}").strip()
                     try: datetime.strptime(end_date_str, "%Y-%m-%d"); break
                     except ValueError: print(f"{C_WARNING}Invalid date format.{C_RESET}")
                holidays = []; add_holidays = input(f"{C_PROMPT}Add holidays? (y/n): {C_RESET}").lower().strip()
                if add_holidays == 'y':
                    print(f"{C_DIM}Enter holiday dates (YYYY-MM-DD), blank line when done.{C_RESET}")
                    while True:
                        h_date_str = input(f"{C_PROMPT} Holiday date: {C_RESET}").strip()
                        if not h_date_str: break
                        try: datetime.strptime(h_date_str, "%Y-%m-%d"); holidays.append(h_date_str)
                        except ValueError: print(f"{C_WARNING}Invalid format.{C_RESET}")
                    print(f"{C_INFO}Using {len(holidays)} custom holidays.{C_RESET}")
                result = calculate_future_attendance(total_p, total_c, end_date_str, holidays); display_future_attendance_results(result)
            elif choice == 4:
                 target_perc = None # Initialize
                 while True: # Loop until valid percentage
                    target_str = input(f"{C_PROMPT}{E_TARGET} Enter Target % (e.g., 75): {C_RESET}").strip()
                    try: # Corrected structure
                        target_perc = float(target_str)
                        if 0 < target_perc <= 100: break
                        else: print(f"{C_WARNING}Target must be > 0 and <= 100.{C_RESET}")
                    except ValueError: print(f"{C_WARNING}Invalid number format. Please enter digits (e.g., 75 or 85.5).{C_RESET}")

                 cls_n, days_n, new_p = calculate_classes_needed_for_target(total_p, total_c, default_schedule, target_perc) # Pass schedule
                 header_text = f" Reaching {target_perc}% Attendance ({default_future_days}-day schedule) "; print(f"\n{C_HEADER}---{header_text}---{C_RESET}")
                 current_perc = (total_p / total_c * 100) if total_c > 0 else 0.0
                 if current_perc >= target_perc: print(f"{C_GREEN}{E_HAPPY} Current ({current_perc:.2f}%) already >= {target_perc}%.{C_RESET}")
                 elif cls_n == float('inf'): print(f"{C_ERROR}{E_ERROR} Impossible to reach {target_perc}% based on schedule.{C_RESET}")
                 elif cls_n > 0:
                     print(f"{C_YELLOW}{E_POINT_RIGHT} Need to attend next {C_BOLD}{cls_n}{C_RESET}{C_YELLOW} classes consecutively.{C_RESET}")
                     if days_n != float('inf'): print(f"{C_YELLOW}   Approx. {C_BOLD}{days_n}{C_RESET}{C_YELLOW} unique future school days (next {default_future_days} days).{C_RESET}")
                     immediate_new_p = (total_p + cls_n) / (total_c + cls_n) * 100 if (total_c + cls_n) > 0 else 0.0
                     print(f"{C_YELLOW}   Immediately after, attendance would be ~{C_BOLD}{immediate_new_p:.2f}%{C_RESET}{C_YELLOW}.{C_RESET}")
                 else: print(f"{C_YELLOW}{E_THINK} Already meet target or no classes needed? Check logic.{C_RESET}")
                 plain_header_len = len(f"---{header_text}---"); print(f"{C_HEADER}{'-' * plain_header_len}{C_RESET}")
            elif choice == 5: display_summary(summary)
            elif choice == 6: toggle_debug_mode() # Toggle debug
            else: print(f"{C_WARNING}{E_WARNING} Invalid choice.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
        except KeyboardInterrupt: print(f"\n{C_YELLOW}{E_WARNING} Menu interrupted.{C_RESET}"); continue
        except Exception as e: print(f"\n{C_ERROR}{E_ERROR} Menu error: {e}\n{C_DIM}{traceback.format_exc()}{C_RESET}"); continue


# === Main Orchestration ===
def main():
    clear_screen()
    print(f"{C_TITLE}{C_BOLD}{'*'*45}{C_RESET}")
    print(f"{C_TITLE}{C_BOLD}*      📊 NIET Attendance Tracker {E_ROCKET}      *{C_RESET}")
    print(f"{C_TITLE}{C_BOLD}{'*'*45}{C_RESET}")

    # --- Get Login Choice ---
    choice = get_login_choice()
    if choice == 0: print(f"{C_INFO}{E_WAVE} Exiting program.{C_RESET}"); return

    jsessionid = None; username = None; attendance_data = None

    if choice == 2:  # Use saved credentials
        username_input, password, was_saved = select_or_enter_credentials(None)  # No need for encryption key
        if not username_input or not password:
            print(f"{C_ERROR}No valid credentials provided. Exiting.{C_RESET}")
            return
            
        if DEBUG_MODE:
            print(f"{C_INFO}Attempting to login via browser...{C_RESET}")
        login_user, new_jsessionid = login_and_extract_selenium(NIET_LOGIN_URL, username_input, password)
        if new_jsessionid:
            jsessionid = new_jsessionid
            username = login_user
            save_jsessionid(jsessionid)
            if not was_saved:
                save_choice = input(f"{C_PROMPT}{E_SAVE} Save credentials for '{C_CYAN}{username}{C_PROMPT}'? (y/n): {C_RESET}").strip().lower()
                if save_choice == 'y':
                    save_credentials(username, password)
        else:
            print(f"{C_ERROR}Login via browser failed.{C_RESET}")
            # Try using saved JSESSIONID as fallback
            saved_jsessionid = load_jsessionid()
            if saved_jsessionid and verify_jsessionid(saved_jsessionid):
                jsessionid = saved_jsessionid
                print(f"{C_SUCCESS}{E_SUCCESS} Using saved session as fallback.{C_RESET}")
            else:
                print(f"{C_ERROR}No valid session available. Please try logging in again.{C_RESET}")
                return

    elif choice == 1:  # Login with new credentials
        if not SELENIUM_AVAILABLE:
            print(f"{C_ERROR}Selenium not available, cannot login via browser. Exiting.{C_RESET}")
            return
            
        username_input, password, was_saved = select_or_enter_credentials(None)  # No need for encryption key
        if not username_input or not password:
            print(f"{C_ERROR}No valid credentials provided. Exiting.{C_RESET}")
            return
            
        if DEBUG_MODE:
            print(f"{C_INFO}Attempting to login via browser...{C_RESET}")
        login_user, new_jsessionid = login_and_extract_selenium(NIET_LOGIN_URL, username_input, password)
        if new_jsessionid:
            jsessionid = new_jsessionid
            username = login_user
            save_jsessionid(jsessionid)
            if not was_saved:
                save_choice = input(f"{C_PROMPT}{E_SAVE} Save credentials for '{C_CYAN}{username}{C_PROMPT}'? (y/n): {C_RESET}").strip().lower()
                if save_choice == 'y':
                    save_credentials(username, password)
        else:
            print(f"{C_ERROR}Login via browser failed.{C_RESET}")
            return

    # --- Fetch Attendance Data (if we have a session ID) ---
    if jsessionid:
        attendance_data = fetch_attendance_data(jsessionid, bypass_ssl_verify=True)
    else:
        print(f"{C_ERROR}Failed to obtain a valid session ID. Cannot fetch data.{C_RESET}")

    # --- Run Tracker (if data was fetched) ---
    if attendance_data:
        run_attendance_tracker(attendance_data)
    else:
        print(f"{C_ERROR}Failed to fetch attendance data. Exiting.{C_RESET}")

def get_login_choice():
    """Displays login options and returns user's choice."""
    while True:
        print(f"\n{C_HEADER}--- {E_LOGIN} Login Options ---{C_RESET}")
        print(f"  {C_CYAN}1{C_RESET}. {E_LOGIN} Login with new credentials")
        print(f"  {C_CYAN}2{C_RESET}. {E_REUSE} Use saved credentials")
        print(f"  {C_CYAN}3{C_RESET}. {E_GEAR} Toggle Debug Mode ({C_GREEN if DEBUG_MODE else C_RED}{'ON' if DEBUG_MODE else 'OFF'}{C_RESET})")
        print(f"  {C_CYAN}0{C_RESET}. {E_LOGOUT} Exit")
        try:
            choice = int(input(f"\n{C_PROMPT}Select an option: {C_RESET}").strip())
            if choice in [0, 1, 2]: return choice
            elif choice == 3: toggle_debug_mode(); continue # Show menu again after toggle
            else: print(f"{C_WARNING}Invalid choice. Please select 0, 1, 2, or 3.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Please enter a number.{C_RESET}")
        except KeyboardInterrupt: print(f"\n{C_YELLOW}Exiting program.{C_RESET}"); return 0

# --- Emojis ---
E_SUCCESS="✅"; E_ERROR="❌"; E_WARNING="⚠️"; E_INFO="ℹ️"; E_PROMPT="👉"; E_CLOCK="⏳"; E_ROCKET="🚀"; E_TARGET="🎯"
E_CALENDAR="📅"; E_BOOK="📚"; E_LOGIN="🔑"; E_LOGOUT="🚪"; E_EYES="👀"; E_CHART_UP="📈"; E_CHART_DOWN="📉"; E_NEUTRAL="😐"
E_HAPPY="😊"; E_SAD="😟"; E_THINK="🤔"; E_STAR="✨"; E_POINT_RIGHT="👉"; E_WAVE="👋"; E_GEAR="⚙️"; E_COMPUTER="💻"
E_SAVE = "💾"; E_REUSE = "🔄"; E_KEY = "🗝️"; E_LOCK = "🔒"; E_UNLOCK = "🔓"
E_PRESENT="👍"; E_ABSENT="👎"; E_OTHER_STATUS="❓"

# --- OS Detection ---
def get_default_browser():
    """Returns the default browser based on the operating system."""
    system = platform.system().lower()
    if system == 'windows':
        return 'edge'
    elif system == 'linux':
        return 'firefox'
    else:
        return 'firefox'  # Default to Firefox for other systems

# === Utility ===
def clear_screen():
    """Cross-platform screen clearing"""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS
        os.system('clear')

# === Loading Animation ===
def _animate(msg="Loading..."):
    frames="|/-\\" ; idx=0
    while not _loading_stop.is_set():
        f=frames[idx%len(frames)]; ln=f"\r{C_PROMPT}{E_CLOCK} {msg} {C_YELLOW}{f}{C_RESET} "; sys.stdout.write(ln); sys.stdout.flush()
        idx+=1; time.sleep(0.15)
    sys.stdout.write('\r'+' '*(len(msg)+10)+'\r'); sys.stdout.flush()

def start_loading(msg="Processing..."):
    global _loading_stop,_loading_thread
    if _loading_thread and _loading_thread.is_alive(): return
    _loading_stop.clear();_loading_thread=threading.Thread(target=_animate,args=(msg,),daemon=True);_loading_thread.start()

def stop_loading(succ_msg=None):
    global _loading_stop,_loading_thread
    if _loading_thread and _loading_thread.is_alive(): _loading_stop.set();_loading_thread.join(0.5)
    _loading_thread=None
    if succ_msg: print(f"{C_SUCCESS}{E_SUCCESS} {succ_msg}{C_RESET}")

if __name__ == "__main__":
    # Dependency checks and warnings
    if not CRYPTOGRAPHY_AVAILABLE:
         print(f"{C_ERROR}{'='*60}{C_RESET}")
         print(f"{C_ERROR}{E_ERROR} Python package 'cryptography' is required for saving passwords securely.")
         print(f"{C_INFO}   Install it using: pip install cryptography")
         print(f"{C_WARNING}   Password saving/loading will be disabled without it.")
         print(f"{C_ERROR}{'='*60}{C_RESET}")
    if not RICH_AVAILABLE:
         print(f"{C_WARNING}{'='*60}{C_RESET}")
         print(f"{C_WARNING}{E_WARNING} Python package 'rich' is recommended for best table display.")
         print(f"{C_INFO}   Install it using: pip install rich")
         if TABULATE_AVAILABLE: print(f"{C_INFO}   Falling back to 'tabulate' for basic tables.")
         else: print(f"{C_ERROR}   'tabulate' also not found. Table display will be minimal.")
         print(f"{C_WARNING}{'='*60}{C_RESET}")
    if not SELENIUM_AVAILABLE:
         print(f"{C_ERROR}{'='*60}{C_RESET}")
         print(f"{C_ERROR}{E_ERROR} Python package 'selenium' is required for browser login.")
         print(f"{C_INFO}   Install it using: pip install selenium beautifulsoup4 webdriver-manager")
         print(f"{C_ERROR}{'='*60}{C_RESET}")
    main()
# --- END OF FILE ---