# --- START OF FILE firefox_new.py ---

# --- START OF FILE firefox_loginnn.py ---

# --- START OF FILE niet_attendance_tracker.py ---

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
import os  # Added os import
import sys  # Added sys import for sys.exit()
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Tuple, Dict, Any # Added typing imports

# === Animation Constants and Utilities ===
SPINNERS = {
    'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
    'line': ['|', '/', '-', '\\'],
    'bounce': ['⠁', '⠂', '⠄', '⡀', '⢀', '⠠', '⠐', '⠈'],
    'rocket': ['🚀 ', ' 🚀', '  🚀', '   🚀', '    🚀', '     🚀', '    🚀', '   🚀', '  🚀', ' 🚀'],
    'stars': ['✨', '⭐', '🌟', '💫', '✨', '⭐', '🌟', '💫']
}

def _create_progress_bar(progress, width=30):
    """Create a simple progress bar string."""
    filled = int(width * progress)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {int(progress * 100)}%"

def _animate_welcome():
    """Display a welcome animation."""
    welcome_text = "NIET ATTENDANCE TRACKER"
    colors = [C_CYAN, C_GREEN, C_YELLOW, C_RED, C_BLUE]
    clear_screen()
    for i in range(len(welcome_text) + 1):
        text = welcome_text[:i]
        color = colors[i % len(colors)]
        print(f"\r{color}{text}{C_RESET}", end='', flush=True)
        time.sleep(0.1)
    print("\n")
    time.sleep(0.5)

def _animate(msg="Loading...", style='dots'):
    """Enhanced animation function with multiple styles."""
    frames = SPINNERS.get(style, SPINNERS['dots'])
    idx = 0
    start_time = time.time()
    
    while not _loading_stop.is_set():
        frame = frames[idx % len(frames)]
        elapsed = time.time() - start_time
        
        if style == 'rocket':
            # Special animation for rocket
            spaces = " " * (idx % 5)
            line = f"\r{spaces}🚀 {msg} {frame}"
        elif style == 'progress':
            # Progress bar animation
            progress = (elapsed % 3) / 3  # 3-second cycle
            bar = _create_progress_bar(progress)
            line = f"\r{msg} {bar}"
        else:
            # Default spinner animation
            line = f"\r{frame} {msg}"
        
        sys.stdout.write(f"{C_CYAN}{line}{C_RESET}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    
    # Clear the line when done
    sys.stdout.write('\r' + ' ' * (len(msg) + 40) + '\r')
    sys.stdout.flush()

def start_loading(msg="Processing...", style='dots'):
    """Start a loading animation with specified style."""
    global _loading_stop, _loading_thread
    if _loading_thread and _loading_thread.is_alive():
        return
    _loading_stop.clear()
    _loading_thread = threading.Thread(target=_animate, args=(msg, style), daemon=True)
    _loading_thread.start()

def stop_loading(succ_msg=None, error_msg=None):
    """Stop the loading animation with optional success or error message."""
    global _loading_stop, _loading_thread
    if _loading_thread and _loading_thread.is_alive():
        _loading_stop.set()
        _loading_thread.join(0.5)
    _loading_thread = None
    
    if error_msg:
        print(f"{C_ERROR}{E_ERROR} {error_msg}{C_RESET}")
    elif succ_msg:
        print(f"{C_SUCCESS}{E_SUCCESS} {succ_msg}{C_RESET}")

# --- Global Variables ---
RICH_AVAILABLE = False
TABULATE_AVAILABLE = False
CRYPTOGRAPHY_AVAILABLE = False
SELENIUM_AVAILABLE = False
DEBUG_MODE = False
_loading_stop = threading.Event()
_loading_thread = None

# --- Cryptography for Password Encryption ---
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    class Fernet: # Dummy class
        def __init__(self, key): pass
        def encrypt(self, data): return data
        def decrypt(self, token): return token

# --- Rich for Table Display ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from rich.panel import Panel
    from rich.align import Align
    import rich.box as box # Import box styles
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    class Console: pass # Dummy class
    class Table: pass # Dummy class
    class Text: pass # Dummy class
    class Panel: pass # Dummy class
    class Align: pass # Dummy class
    print("⚠️ Optional 'rich' library not found. Tables will have basic formatting. (pip install rich)")

# --- Tabulate for Fallback Table Display ---
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    # Define a dummy tabulate function if the module is not installed
    def tabulate(data, headers=None, tablefmt=None, showindex=None): # Dummy function
        """Minimalistic fallback for printing table data if tabulate is not installed."""
        output_lines = []
        output_lines.append("--- Table Data (tabulate/rich not installed) ---")
        col_names = []
        if isinstance(data, pd.DataFrame):
             data_list = data.to_dict('records') # Convert DataFrame for consistency
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            data_list = data
        else:
             output_lines.append(str(data)) # Print simple data as is
             print("\n".join(output_lines)); return

        if data_list:
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
    print("⚠️ Warning: 'colorama' not installed. Colored text disabled. (pip install colorama)")
    C_RESET=C_BRIGHT=C_DIM=C_RED=C_GREEN=C_YELLOW=C_BLUE=""
    C_MAGENTA=C_CYAN=C_WHITE=C_BLACK=C_HEADER=C_TITLE=""
    C_PROMPT=C_ERROR=C_WARNING=C_SUCCESS=C_INFO=C_BOLD=""
    C_LOW=C_MID=C_HIGH=C_SUBJECT=""

# --- Selenium ---
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from bs4 import BeautifulSoup
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print(f"{C_WARNING}⚠️ Warning: Selenium missing. Browser login disabled. (pip install selenium beautifulsoup4 webdriver-manager)")
    class WebDriverException(Exception): pass
    class TimeoutException(Exception): pass


# --- Configuration ---
CREDENTIALS_FILE = "credentials.json"
KEY_FILE = "secret.key" # File to store the encryption key
ATTENDANCE_FILE = "attendance.json" # Corrected spelling
SELENIUM_OUTPUT_FILE = "output_login_page.html"
NIET_LOGIN_URL = "https://nietcloud.niet.co.in/login.htm"
NIET_ATTENDANCE_URL = 'https://nietcloud.niet.co.in/getSubjectOnChangeWithSemId1.json'


# --- Emojis ---
E_SUCCESS="✅"; E_ERROR="❌"; E_WARNING="⚠️"; E_INFO="ℹ️"; E_PROMPT="👉"; E_CLOCK="⏳"; E_ROCKET="🚀"; E_TARGET="🎯"
E_CALENDAR="📅"; E_BOOK="📚"; E_LOGIN="🔑"; E_LOGOUT="🚪"; E_EYES="👀"; E_CHART_UP="📈"; E_CHART_DOWN="📉"; E_NEUTRAL="😐"
E_HAPPY="😊"; E_SAD="😟"; E_THINK="🤔"; E_STAR="✨"; E_POINT_RIGHT="👉"; E_WAVE="👋"; E_GEAR="⚙️"; E_COMPUTER="💻"
E_SAVE = "💾"; E_REUSE = "🔄"; E_KEY = "🗝️"; E_LOCK = "🔒"; E_UNLOCK = "🔓"
E_PRESENT="👍"; E_ABSENT="👎"; E_OTHER_STATUS="❓"

# === Utility ===
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

# === Encryption Functions ===
def generate_key():
    """Generates a new Fernet key and saves it to KEY_FILE."""
    if not CRYPTOGRAPHY_AVAILABLE:
        print(f"{C_ERROR}{E_ERROR} Cryptography library not found. Cannot generate key. (pip install cryptography){C_RESET}")
        return None
    try:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file: key_file.write(key)
        print(f"{C_SUCCESS}{E_KEY} New encryption key generated and saved to '{KEY_FILE}'.{C_RESET}")
        print(f"{C_WARNING}{E_WARNING} IMPORTANT: Back up '{KEY_FILE}' securely! If lost, saved passwords cannot be recovered.{C_RESET}")
        return key
    except IOError as e:
        print(f"{C_ERROR}{E_ERROR} Could not write key file '{KEY_FILE}': {e}{C_RESET}"); return None

def load_key():
    """Loads the Fernet key from KEY_FILE."""
    if not CRYPTOGRAPHY_AVAILABLE: return None
    if not os.path.exists(KEY_FILE):
        print(f"{C_INFO}{E_INFO} Encryption key file ('{KEY_FILE}') not found.{C_RESET}"); return None
    try:
        with open(KEY_FILE, "rb") as key_file: key = key_file.read()
        if len(key) < 40:
             print(f"{C_WARNING}{E_WARNING} Key file '{KEY_FILE}' seems corrupted. Delete it to generate a new one.{C_RESET}"); return None
        return key
    except IOError as e:
        print(f"{C_ERROR}{E_ERROR} Could not read key file '{KEY_FILE}': {e}{C_RESET}"); return None

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
        print(f"{C_ERROR}{E_ERROR} Decryption failed! {C_RESET}\n{C_DIM} Error: {e}. Key file '{KEY_FILE}' might have changed or be corrupt.{C_RESET}"); return None


# === Credentials Management ===
def load_credentials():
    """Loads credentials (usernames and encrypted passwords) from CREDENTIALS_FILE."""
    if not os.path.exists(CREDENTIALS_FILE): return {}
    try:
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f: credentials = json.load(f)
        if not isinstance(credentials, dict):
             print(f"{C_WARNING}{E_WARNING} Credentials file '{CREDENTIALS_FILE}' has invalid format. Starting fresh.{C_RESET}"); return {}
        return credentials
    except (json.JSONDecodeError, IOError) as e:
        print(f"{C_WARNING}{E_WARNING} Error reading credentials file '{CREDENTIALS_FILE}': {e}. Starting fresh.{C_RESET}"); return {}

def save_credentials(credentials_dict):
    """Saves the credentials dictionary (with encrypted passwords) to CREDENTIALS_FILE."""
    try:
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(credentials_dict, f, indent=4)
    except IOError as e:
        print(f"{C_ERROR}{E_ERROR} Could not save credentials to '{CREDENTIALS_FILE}': {e}{C_RESET}")

def select_or_enter_credentials(key):
    """Manages credential selection/entry. Returns (username, password, was_saved)."""
    saved_credentials = load_credentials()
    username = None; password = None; was_saved = False

    while True:
        print(f"\n{C_HEADER}--- {E_LOGIN} Credential Selection ---{C_RESET}")
        options = {}; next_option_num = 1
        if saved_credentials:
            print(f"{C_BLUE}Saved Usernames:{C_RESET}")
            sorted_usernames = sorted(saved_credentials.keys())
            for saved_user in sorted_usernames:
                options[next_option_num] = {'type': 'saved', 'username': saved_user}
                print(f"  {C_CYAN}{next_option_num}{C_RESET}. {saved_user}"); next_option_num += 1
            print("-" * 20)
        options[next_option_num] = {'type': 'new'}; print(f"  {C_CYAN}{next_option_num}{C_RESET}. Enter new username and password"); next_option_num += 1
        options[0] = {'type': 'exit'}; print(f"  {C_CYAN}0{C_RESET}. Exit program")

        try:
            choice = int(input(f"\n{C_PROMPT}Select an option: {C_RESET}").strip())
            if choice == 0: return None, None, False
            if choice in options:
                selected = options[choice]
                if selected['type'] == 'saved':
                    username = selected['username']
                    encrypted_pass = saved_credentials.get(username)
                    if not CRYPTOGRAPHY_AVAILABLE:
                         print(f"{C_ERROR}{E_ERROR} Cryptography library needed. (pip install cryptography){C_RESET}")
                         if input(f"{C_PROMPT}Enter password manually for '{username}'? (y/n): {C_RESET}").lower() == 'y':
                              password = getpass.getpass(f"{C_PROMPT} Password for {C_CYAN}{username}{C_RESET}: "); was_saved = True if password else False
                         if password: print(f"{C_INFO}{E_UNLOCK} Using manually entered password.{C_RESET}"); return username, password, was_saved
                         else: continue
                    elif not key: print(f"{C_ERROR}{E_ERROR} Encryption key not loaded.{C_RESET}"); continue
                    elif encrypted_pass:
                        password = decrypt_password(encrypted_pass, key)
                        if password is not None:
                            print(f"{C_INFO}{E_UNLOCK} Using saved credentials for: {C_CYAN}{username}{C_RESET}"); was_saved = True; return username, password, was_saved
                        else: # Decryption failed
                            if input(f"{C_PROMPT}Decryption failed. Enter password manually for '{username}'? (y/n): {C_RESET}").lower() == 'y':
                                password = getpass.getpass(f"{C_PROMPT} Password for {C_CYAN}{username}{C_RESET}: "); was_saved = True if password else False
                            if password: print(f"{C_INFO}{E_UNLOCK} Using manually entered password.{C_RESET}"); return username, password, was_saved
                            else: continue
                    else: print(f"{C_ERROR}Password data missing for '{username}'.{C_RESET}"); continue
                elif selected['type'] == 'new':
                    username = input(f"{C_PROMPT} Enter NIET Cloud username: {C_RESET}").strip()
                    if not username: print(f"{C_WARNING}Username cannot be empty.{C_RESET}"); continue
                    password = getpass.getpass(f"{C_PROMPT} Enter NIET Cloud password: {C_RESET}")
                    if not password: print(f"{C_WARNING}Password cannot be empty.{C_RESET}"); continue
                    was_saved = False; return username, password, was_saved
            else: print(f"{C_WARNING}Invalid choice number.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid input. Please enter a number.{C_RESET}")
        except KeyboardInterrupt: print(f"\n{C_YELLOW}Credential selection cancelled.{C_RESET}"); return None, None, False


# === Selenium Login ===
def login_and_extract_selenium(url, username, password, browser_choice='firefox', output_filename=SELENIUM_OUTPUT_FILE):
    """Logs in using Selenium, returns username and jsessionid if successful."""
    if not SELENIUM_AVAILABLE:
        print(f"{C_ERROR}{E_ERROR} Selenium unavailable. (pip install selenium beautifulsoup4 webdriver-manager){C_RESET}"); return None, None
    driver = None; jsessionid = None; browser_name = browser_choice.capitalize()
    start_loading(f"{E_GEAR} Initializing {browser_name} WebDriver...")
    try:
        # --- Browser Specific Setup ---
        # (Browser setup code remains the same as before)
        if browser_choice == 'firefox':
            from selenium.webdriver.firefox.options import Options as BrowserOptions; from selenium.webdriver.firefox.service import Service as BrowserService
            DriverClass = webdriver.Firefox; DriverManager = None
            try: from webdriver_manager.firefox import GeckoDriverManager as DriverManager
            except ImportError: print(f"{C_DIM}webdriver-manager optional.{C_RESET}")
            opts = BrowserOptions(); opts.add_argument('--headless'); opts.add_argument("--window-size=1920,1080")
        elif browser_choice == 'edge':
            from selenium.webdriver.edge.options import Options as BrowserOptions; from selenium.webdriver.edge.service import Service as BrowserService
            DriverClass = webdriver.Edge; DriverManager = None
            try: from webdriver_manager.microsoft import EdgeChromiumDriverManager as DriverManager
            except ImportError: print(f"{C_DIM}webdriver-manager optional.{C_RESET}")
            opts = BrowserOptions(); opts.add_argument('--headless'); opts.add_argument('--disable-gpu'); opts.add_argument("--window-size=1920,1080"); opts.add_argument("--log-level=3"); opts.add_experimental_option('excludeSwitches', ['enable-logging'])
        elif browser_choice == 'chrome':
            from selenium.webdriver.chrome.options import Options as BrowserOptions; from selenium.webdriver.chrome.service import Service as ChromeService; BrowserService = ChromeService
            DriverClass = webdriver.Chrome; DriverManager = None
            try: from webdriver_manager.chrome import ChromeDriverManager as DriverManager
            except ImportError: print(f"{C_DIM}webdriver-manager optional.{C_RESET}")
            opts = BrowserOptions(); opts.add_argument('--headless'); opts.add_argument('--disable-gpu'); opts.add_argument("--window-size=1920,1080"); opts.add_argument("--log-level=3"); opts.add_experimental_option('excludeSwitches', ['enable-logging']); opts.add_argument("--no-sandbox"); opts.add_argument("--disable-dev-shm-usage")
        else: stop_loading(); print(f"{C_ERROR}{E_ERROR} Unsupported browser: {browser_choice}{C_RESET}"); return None, None

        # --- WebDriver Initialization ---
        # (WebDriver initialization code remains the same)
        try:
            if DriverManager: svc = BrowserService(DriverManager().install()); os.environ['WDM_LOG_LEVEL'] = '0'; os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
            else: svc = BrowserService() # Try system driver
            driver = DriverClass(service=svc, options=opts)
        except Exception as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} {browser_name} WebDriver setup failed: {e}{C_RESET}\n{C_DIM} Ensure {browser_name} installed & correct driver in PATH or install webdriver-manager.{C_RESET}"); return None, None

        # --- Login Steps ---
        stop_loading(f"{E_COMPUTER} {browser_name} WebDriver Initialized.")
        print(f"{C_INFO}{E_LOGIN} Logging into: {C_CYAN}{url}{C_RESET} using {browser_name}")
        start_loading(f"{E_EYES} Opening page..."); driver.get(url); stop_loading()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "j_username"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "j_password"))).send_keys(password)
        print(f"{C_INFO}   Credentials entered.")
        start_loading(f"{E_ROCKET} Submitting..."); WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        try: WebDriverWait(driver, 30).until(EC.any_of(EC.url_contains("Dashboard"), EC.presence_of_element_located((By.LINK_TEXT, "Logout")), EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Welcome')]")))); stop_loading(f"{E_SUCCESS} Login submitted.")
        except TimeoutException: stop_loading(); print(f"{C_WARNING}{E_WARNING} Post-login confirmation timeout. Check {output_filename}.")
        except WebDriverException as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} Error waiting for login confirmation: {e}{C_RESET}")

        # ******** FIX START ********
        # Correctly indented block for saving HTML
        try:
            page_source_html = driver.page_source # Get source first
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(page_source_html)
            print(f"{C_DIM}   HTML saved to {output_filename}{C_RESET}")
        except IOError as e:
            print(f"{C_WARNING}Could not save HTML output: {e}{C_RESET}")
        # ******** FIX END ********

        cookies = driver.get_cookies(); jsessionid = next((c['value'] for c in cookies if c['name'] == 'JSESSIONID'), None)
        if jsessionid: print(f"{C_SUCCESS}{E_SUCCESS} JSESSIONID obtained.")
        else: print(f"{C_ERROR}{E_ERROR} JSESSIONID NOT found. Login FAILED? Check {output_filename}.{C_RESET}"); return None, None
    except (TimeoutException, WebDriverException, Exception) as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} Selenium Error ({browser_name}): {e}{C_RESET}\n{C_DIM}{traceback.format_exc()}{C_RESET}"); jsessionid = None
    finally:
        if driver:
            start_loading(f"{E_LOGOUT} Closing {browser_name}...");
            try: driver.quit()
            except Exception as quit_err: print(f"{C_WARNING}Error closing {browser_name}: {quit_err}{C_RESET}")
            # Ensure stop_loading is called even if quit fails
            stop_loading(f"{E_LOGOUT} {browser_name} Closed.")
        else: # Ensure stop_loading is called if driver initialization failed earlier
             if _loading_thread and _loading_thread.is_alive(): stop_loading()


    return username if jsessionid else None, jsessionid

# === Attendance Data Fetching ===
def fetch_attendance_data(jsessionid, bypass_ssl_verify=False):
    """Fetches attendance data using JSESSIONID. Can bypass SSL verification."""
    if not jsessionid: print(f"{C_ERROR}{E_ERROR} JSESSIONID required.{C_RESET}"); return None
    cookies = {'JSESSIONID': jsessionid}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36', 'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-Requested-With': 'XMLHttpRequest', 'Referer': 'https://nietcloud.niet.co.in/studentCourseFileNew.htm'}
    params = {'termId': '2', 'refreshData': '0'}
    url = NIET_ATTENDANCE_URL
    print(f"\n{C_INFO}{E_ROCKET} Fetching attendance data...{C_RESET}")
    start_loading("Requesting from NIET Cloud...")
    data, response, raw_text = None, None, ""
    verify_ssl = True
    if bypass_ssl_verify:
        print(f"{C_WARNING}{E_WARNING} Bypassing SSL certificate verification.{C_RESET}")
        try: urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except AttributeError: pass
        verify_ssl = False
    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers, timeout=45, verify=verify_ssl)
        stop_loading()
        content_type = response.headers.get('Content-Type', '').lower()
        try: raw_text = response.content.decode('utf-8', errors='replace')
        except Exception: raw_text = str(response.content) # Fallback

        # Optional Debug Prints can remain commented out or enabled as needed
        # print(f"\n{C_DIM}--- Request Debug Info ---")
        # print(f"URL: {response.url}\nStatus Code: {response.status_code}\nContent-Type: {content_type}")
        # print(f"--- Response Body (First 500 chars) ---\n{C_YELLOW}{raw_text[:500]}{C_RESET}\n--- End Debug Info ---{C_RESET}")

        response.raise_for_status() # Check for HTTP errors AFTER getting potential content

        if 'application/json' not in content_type:
             print(f"{C_ERROR}{E_ERROR} Server didn't return JSON (Content-Type: '{content_type}'). Cannot parse.{C_RESET}")
             # ******** FIX START ********
             try:
                 with open("non_json_response.txt", "w", encoding="utf-8") as f:
                     f.write(raw_text)
                 # This print should be outside the 'with' block if it's just confirming the save
                 print(f"{C_INFO}Unexpected response saved to non_json_response.txt{C_RESET}")
             except Exception as save_err:
                 print(f"{C_WARNING}Could not save non-JSON response: {save_err}{C_RESET}")
             # ******** FIX END ********
             return None

        # If content type IS JSON, proceed to decode
        data = response.json()
        try:
            with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
            print(f"{C_SUCCESS}{E_SUCCESS} Fresh data saved to '{ATTENDANCE_FILE}'.{C_RESET}")
        except (IOError, TypeError) as e: print(f"{C_WARNING}{E_WARNING} Could not save data to {ATTENDANCE_FILE}: {e}{C_RESET}")

    except requests.exceptions.Timeout: print(f"{C_ERROR}{E_ERROR} Request timed out.{C_RESET}")
    except requests.exceptions.SSLError as e: print(f"{C_ERROR}{E_ERROR} SSL Error: {e}.{C_YELLOW} Server cert issue?{C_RESET}")
    except requests.exceptions.ConnectionError as e: print(f"{C_ERROR}{E_ERROR} Connection Error: {e}.{C_INFO} Check network/firewall.{C_RESET}")
    except requests.exceptions.HTTPError as e: print(f"{C_ERROR}{E_ERROR} HTTP Error: {e}. {C_YELLOW} Check JSESSIONID validity.{C_RESET}" if response and response.status_code in [401, 403] else "")
    except requests.exceptions.RequestException as e: print(f"{C_ERROR}{E_ERROR} Network Error: {e}{C_RESET}")
    except json.JSONDecodeError as e:
        print(f"{C_ERROR}{E_ERROR} Failed to decode JSON response: {e}{C_RESET}\n{C_INFO}Check debug output or saved 'json_decode_error_response.txt'.{C_RESET}")
        if raw_text:
            # ******** FIX START (Repeated Fix - Ensure correct indentation here too) ********
            try:
                with open("json_decode_error_response.txt", "w", encoding="utf-8") as f:
                    f.write(raw_text)
                print(f"{C_INFO}Problematic response saved to json_decode_error_response.txt{C_RESET}")
            except Exception as save_err:
                print(f"{C_WARNING}Could not save error response: {save_err}{C_RESET}")
            # ******** FIX END ********
    except Exception as e: print(f"{C_ERROR}{E_ERROR} Unexpected error during fetch: {e}\n{C_DIM}{traceback.format_exc()}{C_RESET}")
    finally:
        # Ensure loading stops even if there was an error before this point
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

# --- MODIFIED: extract_summary_data (for rich) ---
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
                'Code': f"{subj_code}", # Plain code
                f'{E_BOOK} Course': f"{subj_name}", # Plain name
                'Count': f"{p}/{t}",
                f'{E_CHART_UP} %': perc_s, # Plain percentage string
                ' ': emoji, # Emoji
                '_style': rich_style # Internal key for rich style
            })
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
        'Code': '',
        f'{E_BOOK} Course': 'TOTAL',
        'Count': f"{total_p}/{total_c}",
        f'{E_CHART_UP} %': ov_perc_s,
        ' ': ov_emoji,
        '_style': "bold white" # Style for TOTAL row (overrides percentage color)
    })
    return summary,total_p,total_c

# --- MODIFIED: extract_detailed_attendance (for rich) ---
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
                else: status_text, status_emoji, rich_style = st, E_OTHER_STATUS, "yellow" # Unknown status text
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
    
    # Clear screen before displaying header
    clear_screen()

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
            style = row_dict['_style'] # Get rich style name
            # Map rich style to Colorama approx
            color_c = ""
            if style == "bold red": color_c = C_LOW + C_BOLD
            elif style == "bold yellow": color_c = C_MID + C_BOLD
            elif style == "bold green": color_c = C_HIGH + C_BOLD
            elif style == "dim": color_c = C_DIM
            elif style == "bold white": color_c = C_WHITE + C_BOLD

            # Special handling for TOTAL row where style applies to whole row
            if row_dict[f'{E_BOOK} Course'] == 'TOTAL':
                 tab_row = {
                     'Code': f"{color_c}{row_dict['Code']}{C_RESET}",
                     f'{E_BOOK} Course': f"{color_c}{row_dict[f'{E_BOOK} Course']}{C_RESET}",
                     'Count': f"{color_c}{row_dict['Count']}{C_RESET}",
                     f'{E_CHART_UP} %': f"{color_c}{perc_s}{C_RESET}",
                     ' ': f"{color_c}{row_dict[' ']}{C_RESET}"
                 }
            else: # Normal row - color only percentage
                 tab_row = {
                     'Code': f"{C_DIM}{row_dict['Code']}{C_RESET}", # Dim code
                     f'{E_BOOK} Course': f"{C_SUBJECT}{row_dict[f'{E_BOOK} Course']}{C_RESET}", # Subject color
                     'Count': row_dict['Count'],
                     f'{E_CHART_UP} %': f"{color_c}{perc_s}{C_RESET}" if color_c else perc_s,
                     ' ': row_dict[' ']
                 }
            tabulate_data.append(tab_row)
        try:
            df=pd.DataFrame(tabulate_data)
            print(f"\n{C_HEADER}{E_STAR}=== Attendance Summary ==={E_STAR}{C_RESET}\n")
            print(tabulate(df,headers='keys',tablefmt='grid',showindex=False))
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
    
    # Clear screen before displaying header
    clear_screen()

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
            status_text = row_dict['Status']
            style = row_dict['_style'] # Get rich style name
            color_c = "" # Map rich style to Colorama approx
            if style == "green": color_c = C_GREEN
            elif style == "red": color_c = C_RED
            elif style == "yellow": color_c = C_YELLOW
            tab_row = {
                'Sr': f"{C_DIM}{row_dict['Sr']}{C_RESET}",
                f'{E_CALENDAR} Date': row_dict[f'{E_CALENDAR} Date'],
                f'{E_CLOCK} Time': row_dict[f'{E_CLOCK} Time'],
                'Session': row_dict['Session'],
                'Status': f"{color_c}{status_text}{C_RESET}" if color_c else status_text,
                ' ': row_dict[' ']
            }
            tabulate_data.append(tab_row)
        try:
            df=pd.DataFrame(tabulate_data)
            subj_d=f"{C_SUBJECT}{C_BOLD}{subject}{C_RESET}"
            print(f"\n{C_HEADER}=== {E_EYES} Details: {subj_d} ==={C_RESET}\n")
            print(tabulate(df,headers='keys',tablefmt='grid',showindex=False))
        except Exception as e: print(f"{C_ERROR}{E_ERROR} Tabulate error: {e}\n{C_DIM}Data: {details_data}{C_RESET}")
    else: # Basic fallback
         subj_d=f"{C_SUBJECT}{C_BOLD}{subject}{C_RESET}"
         print(f"\n{C_HEADER}=== {E_EYES} Details: {subj_d} ==={C_RESET}\n")
         headers = list(details_data[0].keys()) if details_data else []
         headers = [h for h in headers if not h.startswith('_')]
         if headers: print(" | ".join(headers))
         for row_dict in details_data: print(" | ".join(str(row_dict.get(h, '')) for h in headers))


# === Calculations (Unaffected by rich, kept as is) ===
def generate_future_schedule(days_ahead: int, holidays: set = None) -> List[Tuple[date, int]]:
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

def calculate_classes_needed_for_target(total_present: int, total_classes: int, future_schedule: List[Tuple[date, int]], target_percentage: float = 85.0) -> Tuple[int, int, float]:
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

def calculate_leave_allowance(total_present: int, total_classes: int, future_schedule: List[Tuple[date, int]], target_percentage: float = 85.0) -> Dict[str, any]:
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


# === Calculation Display (Unaffected by rich, kept as is) ===
def display_leave_allowance_results(result: Dict[str, any], total_p: int, total_c: int, future_schedule: List[Tuple[date, int]], target_percentage: float):
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
        cls_n, days_n, _ = calculate_classes_needed_for_target(total_p, total_c, future_schedule, target_percentage)
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
    
    # Clear screen before displaying header
    clear_screen()

    print(f"\n{C_HEADER}{E_CALENDAR}=== Future Attendance Projection ==={C_RESET}\n")
    print(f"Current Attendance: {result['current_total']} ({result['current_percentage']}%)")
    print(f"Total Future Classes Until End Date: {result['future_classes']}")
    print(f"Projected Total Classes by End Date: {result['future_total_classes']}")

    if result['classes_needed_85'] != 0:
        if result['classes_needed_85'] == float('inf'): print(f"\n{C_ERROR}{E_CHART_DOWN} Impossible to reach 85% overall by end date based on schedule.{C_RESET}")
        elif result['classes_needed_85'] > 0: print(f"\n{C_YELLOW}{E_TARGET} To reach 85% overall, must attend >= {C_BOLD}{result['classes_needed_85']}{C_RESET}{C_YELLOW} of the {result['future_classes']} future classes.{C_RESET}")
    else: print(f"\n{C_GREEN}{E_HAPPY} Projected to be >= 85% by end date if attending all future classes.{C_RESET}")

    print(f"\n{C_BLUE}{E_THINK} Projections based on different future attendance rates:{C_RESET}")
    scen_data = []
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
            perc_s = row_dict[f'{E_CHART_UP}Proj. %']
            style = row_dict['_style'] # Get rich style name
            color_c = "" # Map rich style to Colorama approx
            if style == "bold red": color_c = C_LOW + C_BOLD
            elif style == "bold yellow": color_c = C_MID + C_BOLD
            elif style == "bold green": color_c = C_HIGH + C_BOLD
            elif style == "dim": color_c = C_DIM
            tab_row = { h: row_dict[h] for h in row_dict if not h.startswith('_') } # Copy relevant keys
            # Color the percentage cell for tabulate
            tab_row[f'{E_CHART_UP}Proj. %'] = f"{color_c}{perc_s}{C_RESET}" if color_c else perc_s
            tabulate_data.append(tab_row)
        try:
            df = pd.DataFrame(tabulate_data)
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
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
                 display_leave_allowance_results(result, total_p, total_c, default_schedule, target_leave)
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
                        # ... (rest of the choices) ...

            elif choice == 4:
                 target_perc = None # Initialize target_perc
                 while True: # Loop until valid percentage is entered
                    target_str = input(f"{C_PROMPT}{E_TARGET} Enter Target % (e.g., 75): {C_RESET}").strip()
                    # --- FIX START ---
                    try:
                        # Step 1: Try conversion
                        target_perc = float(target_str)
                        # Step 2: If conversion succeeds, validate range
                        if 0 < target_perc <= 100:
                            break # Valid input, exit the while loop
                        else:
                            print(f"{C_WARNING}Target must be > 0 and <= 100.{C_RESET}")
                            # Loop continues automatically
                    except ValueError:
                        # Step 3: Handle conversion error
                        print(f"{C_WARNING}Invalid number format. Please enter digits (e.g., 75 or 85.5).{C_RESET}")
                        # Loop continues automatically
                    # --- FIX END ---

                 # --- Code continues only after a valid target_perc is obtained ---
                 cls_n, days_n, new_p = calculate_classes_needed_for_target(total_p, total_c, default_schedule, target_perc)

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

            # ... (rest of the choices and loop) ...
            elif choice == 5: display_summary(summary)
            else: print(f"{C_WARNING}{E_WARNING} Invalid choice.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
        except KeyboardInterrupt: print(f"\n{C_YELLOW}{E_WARNING} Menu interrupted.{C_RESET}"); continue
        except Exception as e: print(f"\n{C_ERROR}{E_ERROR} Menu error: {e}\n{C_DIM}{traceback.format_exc()}{C_RESET}"); continue


# === Main Orchestration ===
def main():
    """Main function to run the NIET Attendance Tracker."""
    # Check if running through alias
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-alias":
        setup_alias()
        return
    
    # Clear screen before displaying header
    clear_screen()
    
    # Display welcome animation
    _animate_welcome()
    
    # Initialize console for rich output
    console = Console()
    
    # Create title
    title = Text("📊 NIET ATTENDANCE TRACKER", style="bold magenta", justify="center")
    
    # Create header panel
    header_panel = Panel(
        Align(title, align="center"),
        border_style="magenta",
        padding=(1, 2)
    )
    
    # Display header
    console.print(header_panel)
    
    # Display contributors with animation
    print("\nContributors:")
    start_loading("Fetching contributors...", style='stars')
    contributors = fetch_github_contributors()
    stop_loading()
    
    if contributors:
        # Group contributors into rows of 3
        for i in range(0, len(contributors), 3):
            row = contributors[i:i+3]
            contributor_texts = []
            for j, contributor in enumerate(row):
                style, emoji, color = get_contributor_style(i + j)
                contributor_texts.append(f"{emoji} {color}{contributor}{C_RESET}")
            print("  " + "  |  ".join(contributor_texts))
    else:
        print(f"{C_WARNING}  No contributors found or failed to fetch.{C_RESET}")
    
    print("\nRepository: https://github.com/iamawanishmaurya/NIET-Attendance-Tracker/")
    
    # Initialize loading animation
    start_loading("Initializing...", style='dots')
    time.sleep(0.5)
    stop_loading()
    
    # --- Dependency Checks ---
    if not RICH_AVAILABLE and not TABULATE_AVAILABLE:
        print(f"{C_WARNING}{E_WARNING} Neither 'rich' nor 'tabulate' found. Table display will be very basic. (pip install rich tabulate){C_RESET}")
    if not CRYPTOGRAPHY_AVAILABLE:
        print(f"{C_ERROR}{E_ERROR} Required 'cryptography' not found. Password saving disabled! (pip install cryptography){C_RESET}")

    encryption_key = load_key()
    attendance_data = None; jsessionid = None

    # --- Browser Selection ---
    browser_options = ['firefox', 'edge', 'chrome']
    print(f"\n{C_BLUE}{E_POINT_RIGHT} Select Browser for Login (Option 1):{C_RESET}")
    for i, browser in enumerate(browser_options, 1): print(f"  {C_CYAN}{i}{C_RESET}. {browser.capitalize()}")
    selected_browser = 'firefox' # Default
    while True:
        b_choice_str = input(f"{C_PROMPT}Browser number (1-{len(browser_options)}, default 1): {C_RESET}").strip()
        if not b_choice_str: break
        try:
            b_idx = int(b_choice_str)
            if 1 <= b_idx <= len(browser_options): selected_browser = browser_options[b_idx - 1]; print(f"{C_INFO}Selected: {selected_browser.capitalize()}{C_RESET}"); break
            else: print(f"{C_WARNING}Invalid browser number.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")

    # --- Data Source Selection ---
    print(f"\n{C_BLUE}{E_POINT_RIGHT} How to get attendance data?{C_RESET}")
    options_list = [
        (f"{E_COMPUTER}Log in via Browser ({selected_browser.capitalize()})", SELENIUM_AVAILABLE, 1),
        (f"{E_LOGIN}Use existing JSESSIONID", True, 2),
        (f"{E_BOOK}Load from '{ATTENDANCE_FILE}'", True, 3) ]
    for i, (text, enabled, _) in enumerate(options_list, 1): print(f"  {C_CYAN}{i}{C_RESET}. {text}" if enabled else f"  {C_DIM}{i}. {text} (Disabled){C_RESET}")
    selected_option_code = None
    while selected_option_code is None:
        try:
            choice = int(input(f"\n{C_PROMPT}Enter choice for data source: {C_RESET}").strip())
            if 1 <= choice <= len(options_list):
                 if not options_list[choice-1][1]: print(f"{C_ERROR}{E_ERROR} Option disabled.{C_RESET}"); continue
                 selected_option_code = options_list[choice-1][2]; break
            else: print(f"{C_WARNING}Invalid choice number.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
        except KeyboardInterrupt: print("\n{C_YELLOW}Exiting program.{C_RESET}"); sys.exit(0)
    print("-" * 40)

    # --- Process Data Source Choice ---
    active_username, active_password = None, None
    if selected_option_code == 1: # Selenium Login
        print(f"{C_HEADER}--- {E_LOGIN} Browser Login ({selected_browser.capitalize()}) ---{C_RESET}")
        username_to_use, password_to_use, was_saved = select_or_enter_credentials(encryption_key)
        if username_to_use and password_to_use:
            active_username, active_password = username_to_use, password_to_use
            login_username, jsessionid = login_and_extract_selenium(NIET_LOGIN_URL, username_to_use, password_to_use, browser_choice=selected_browser)
            if jsessionid and login_username:
                 if login_username != active_username: print(f"{C_WARNING}Username mismatch? Got '{login_username}'.{C_RESET}"); active_username = login_username
                 if CRYPTOGRAPHY_AVAILABLE:
                     if encryption_key is None: print(f"{C_INFO}Generating encryption key...{C_RESET}"); encryption_key = generate_key()
                     if encryption_key:
                         save_choice = input(f"{C_PROMPT}{E_SAVE} Save/Update credentials for '{C_CYAN}{active_username}{C_PROMPT}'? (y/n): {C_RESET}").strip().lower()
                         if save_choice == 'y':
                             encrypted_pass = encrypt_password(active_password, encryption_key)
                             if encrypted_pass != active_password:
                                 current_credentials = load_credentials(); current_credentials[active_username] = encrypted_pass; save_credentials(current_credentials)
                                 print(f"{C_SUCCESS}{E_LOCK} Credentials for '{active_username}' saved/updated securely.{C_RESET}")
                             else: print(f"{C_ERROR}Encryption failed. Not saved.{C_RESET}")
                     else: print(f"{C_WARNING}Key error. Cannot save credentials.{C_RESET}")
                 else: print(f"{C_INFO}Cryptography disabled. Cannot save credentials.{C_RESET}")
                 # Fetch Data after login
                 attendance_data = fetch_attendance_data(jsessionid, bypass_ssl_verify=False)
                 if not attendance_data:
                      print(f"\n{C_WARNING}{E_WARNING} Initial fetch failed. Retrying with SSL bypass...{C_RESET}")
                      attendance_data = fetch_attendance_data(jsessionid, bypass_ssl_verify=True)
                      if not attendance_data: print(f"\n{C_WARNING}{E_WARNING} Fetch failed. Trying local file...{C_RESET}"); attendance_data = load_attendance_data()
            else: # Login failed
                 print(f"{C_ERROR}{E_ERROR} Browser login failed.{C_RESET}")
                 if input(f"{C_PROMPT}Try loading from '{ATTENDANCE_FILE}'? (y/n): {C_RESET}").lower() == 'y': attendance_data = load_attendance_data()
        else: print(f"{C_INFO}Login cancelled.{C_RESET}"); sys.exit(0)
    elif selected_option_code == 2: # Existing JSESSIONID
        print(f"{C_HEADER}--- {E_LOGIN} Use Existing JSESSIONID ---{C_RESET}")
        jsessionid_input = input(f"{C_PROMPT} Enter JSESSIONID: {C_RESET}").strip()
        if jsessionid_input:
            jsessionid = jsessionid_input
            attendance_data = fetch_attendance_data(jsessionid, bypass_ssl_verify=False)
            if not attendance_data:
                 print(f"\n{C_WARNING}{E_WARNING} Fetch failed. Retrying with SSL bypass...{C_RESET}")
                 attendance_data = fetch_attendance_data(jsessionid, bypass_ssl_verify=True)
                 if not attendance_data: print(f"\n{C_WARNING}{E_WARNING} Fetch failed. Trying local file...{C_RESET}"); attendance_data = load_attendance_data()
        else: print(f"{C_WARNING}No JSESSIONID. Trying local file...{C_RESET}"); attendance_data = load_attendance_data()
    elif selected_option_code == 3: # Load from file
        print(f"{C_HEADER}--- {E_BOOK} Load from File ---{C_RESET}")
        file_path = input(f"{C_PROMPT} File path (blank for '{ATTENDANCE_FILE}'): {C_RESET}").strip()
        target_file = file_path if file_path else ATTENDANCE_FILE
        attendance_data = load_attendance_data(target_file)

    # --- Run tracker ---
    if attendance_data:
        try: run_attendance_tracker(attendance_data)
        except KeyboardInterrupt: print(f"\n{C_YELLOW}{E_WAVE} Exiting program.{C_RESET}")
        except Exception as e: print(f"\n{C_ERROR}{E_ERROR} Critical error: {e}\n{C_DIM}{traceback.format_exc()}{C_RESET}"); sys.exit(1)
    else: print(f"\n{C_ERROR}{E_ERROR} Failed to obtain attendance data. Cannot proceed.{C_RESET}"); sys.exit(1)

    print(f"\n{C_TITLE}--- {E_WAVE} Tracker Finished ---{C_RESET}")

# === GitHub Contributors ===
def fetch_github_contributors():
    """Fetches contributor usernames from the GitHub API."""
    try:
        # GitHub API endpoint for contributors
        url = "https://api.github.com/repos/iamawanishmaurya/NIET-Attendance-Tracker/contributors"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'NIET-Attendance-Tracker'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Extract only usernames from the response
            contributors = [contributor['login'] for contributor in response.json()]
            return contributors
        else:
            print(f"{C_WARNING}{E_WARNING} Failed to fetch contributors from GitHub API. Status code: {response.status_code}{C_RESET}")
            return []  # Return empty list if API call fails
            
    except Exception as e:
        if DEBUG_MODE:
            print(f"{C_ERROR}{E_ERROR} Error fetching contributors: {e}{C_RESET}")
            print(f"{C_DIM}{traceback.format_exc()}{C_RESET}")
        return []  # Return empty list on error

def get_contributor_style(index):
    """Returns a style, emoji, and random color combination based on contributor index."""
    # Define color styles and their corresponding colors
    styles = [
        ("bold yellow", "👑", C_YELLOW),   # Founder style
        ("bold green", "🚀", C_GREEN),    # Developer style
        ("bold blue", "💡", C_BLUE),     # Developer style
        ("bold magenta", "⚡", C_MAGENTA),  # Developer style
        ("bold cyan", "🌟", C_CYAN),     # New contributor style
        ("bold red", "🎯", C_RED),      # New contributor style
        ("bold white", "💫", C_WHITE),    # New contributor style
        ("bold yellow", "🎨", C_YELLOW),   # New contributor style
        ("bold green", "🔮", C_GREEN),    # New contributor style
        ("bold blue", "🎭", C_BLUE),     # New contributor style
    ]
    
    # Get style based on index, cycling through the list if needed
    style_index = index % len(styles)
    return styles[style_index]

# === Alias Setup ===
def setup_alias():
    """Sets up the 'niet' alias for the script."""
    try:
        # Get the absolute path of the script
        script_path = os.path.abspath(__file__)
        env_dir = os.path.expanduser("~/niet_env")
        
        # Create virtual environment if it doesn't exist
        if not os.path.exists(env_dir):
            print(f"{C_INFO}Creating virtual environment...{C_RESET}")
            os.system(f"python3 -m venv {env_dir}")
        
        # Add alias to bashrc
        bashrc_path = os.path.expanduser("~/.bashrc")
        alias_cmd = f"alias niet='source {env_dir}/bin/activate && python {script_path}'"
        
        # Check if alias already exists
        with open(bashrc_path, 'r') as f:
            if alias_cmd not in f.read():
                with open(bashrc_path, 'a') as f:
                    f.write(f"\n{alias_cmd}\n")
                print(f"{C_SUCCESS}Alias added to ~/.bashrc{C_RESET}")
            else:
                print(f"{C_INFO}Alias already exists in ~/.bashrc{C_RESET}")
        
        # Add alias to zshrc if it exists
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(zshrc_path):
            with open(zshrc_path, 'r') as f:
                if alias_cmd not in f.read():
                    with open(zshrc_path, 'a') as f:
                        f.write(f"\n{alias_cmd}\n")
                    print(f"{C_SUCCESS}Alias added to ~/.zshrc{C_RESET}")
                else:
                    print(f"{C_INFO}Alias already exists in ~/.zshrc{C_RESET}")
        
        print(f"\n{C_SUCCESS}✅ Alias setup completed.{C_RESET}")
        print(f"{C_INFO}To use the 'niet' command, please restart your terminal.{C_RESET}")
        
    except Exception as e:
        print(f"{C_ERROR}Error setting up alias: {e}{C_RESET}")
        if DEBUG_MODE:
            print(f"{C_DIM}{traceback.format_exc()}{C_RESET}")

if __name__ == "__main__":
    # Check if running through alias
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-alias":
        setup_alias()
    else:
        # Prompt user about missing optional dependencies before starting fully
        if not CRYPTOGRAPHY_AVAILABLE:
            print(f"{C_ERROR}{'='*60}{C_RESET}")
            print(f"{C_ERROR}{E_ERROR} Python package 'cryptography' is recommended for saving passwords.")
            print(f"{C_INFO}   Install it using: pip install cryptography")
            print(f"{C_WARNING}   Password saving/loading is disabled without it.")
            print(f"{C_ERROR}{'='*60}{C_RESET}")
        if not RICH_AVAILABLE:
            print(f"{C_WARNING}{'='*60}{C_RESET}")
            print(f"{C_WARNING}{E_WARNING} Python package 'rich' is recommended for best table display.")
            print(f"{C_INFO}   Install it using: pip install rich")
            if TABULATE_AVAILABLE: print(f"{C_INFO}   Falling back to 'tabulate' for basic tables.")
            else: print(f"{C_ERROR}   'tabulate' also not found. Table display will be minimal.")
            print(f"{C_WARNING}{'='*60}{C_RESET}")
        main()
# --- END OF FILE ---