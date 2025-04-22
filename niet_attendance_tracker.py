import json
import pandas as pd
import os
import requests
from datetime import datetime, timedelta, date
# from tabulate import tabulate # Tabulate imported below after checking
import math
import sys
import time
import threading
import getpass # For password input

# --- Configuration ---
CREDENTIALS_FILE = "credentials.json"
ATTENDANCE_FILE = "attendence.json"
SELENIUM_OUTPUT_FILE = "output_login_page.html"
NIET_LOGIN_URL = "https://nietcloud.niet.co.in/login.htm"
NIET_ATTENDANCE_URL = 'https://nietcloud.niet.co.in/getSubjectOnChangeWithSemId1.json'

# --- Check and Import Tabulate ---
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    # Define a dummy tabulate function if the module is not installed
    def tabulate(data, headers=None, tablefmt=None, showindex=None): # Dummy function
        """Minimalistic fallback for printing table data if tabulate is not installed."""
        output_lines = []
        # Simple fallback if tabulate is missing
        output_lines.append("--- Table Data (tabulate not installed) ---")
        col_names = []
        if isinstance(data, pd.DataFrame):
             col_names = list(data.columns)
             output_lines.append(", ".join(col_names))
             for _, row in data.iterrows():
                 output_lines.append(", ".join(map(str, row.tolist())))
        elif isinstance(data, list) and data:
             if isinstance(data[0], dict):
                 col_names = list(data[0].keys())
                 output_lines.append(", ".join(col_names))
                 for row_dict in data:
                      output_lines.append(", ".join(map(str, row_dict.values())))
             else: # Handle list of lists/tuples maybe? For now, just print items
                 for row in data:
                     output_lines.append(str(row))
        else:
             output_lines.append(str(data))

        output_lines.append("--------------------------------------------")
        print("\n".join(output_lines)) # Print the generated lines
        return "" # Return empty string to avoid errors where print result might be expected


# --- Colorama ---
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
    # Optional: Brief confirmation message (cleared quickly)
    # print(f"{C_GREEN}Colorama active ✅{C_RESET}", end='\r'); time.sleep(0.1); print("                      ", end='\r')
except ImportError:
    print("⚠️ Warning: 'colorama' not installed. Styles disabled. (pip install colorama)")
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
    # --- *** CORRECTED DUMMY CLASS DEFINITIONS *** ---
    class WebDriverException(Exception):
        """Dummy Exception for when Selenium is not installed."""
        pass
    class TimeoutException(Exception):
        """Dummy Exception for when Selenium is not installed."""
        pass
    # --- *** END OF CORRECTION *** ---

# --- Emojis ---
E_SUCCESS="✅"; E_ERROR="❌"; E_WARNING="⚠️"; E_INFO="ℹ️"; E_PROMPT="👉"; E_CLOCK="⏳"; E_ROCKET="🚀"; E_TARGET="🎯"
E_CALENDAR="📅"; E_BOOK="📚"; E_LOGIN="🔑"; E_LOGOUT="🚪"; E_EYES="👀"; E_CHART_UP="📈"; E_CHART_DOWN="📉"; E_NEUTRAL="😐"
E_HAPPY="😊"; E_SAD="😟"; E_THINK="🤔"; E_STAR="✨"; E_POINT_RIGHT="👉"; E_WAVE="👋"; E_GEAR="⚙️"; E_COMPUTER="💻"
E_SAVE = "💾"; E_REUSE = "🔄"

# === Utility ===
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

# === Loading Animation ===
_loading_stop=threading.Event(); _loading_thread=None
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

# === Credentials Management ===
def load_saved_username():
    if not os.path.exists(CREDENTIALS_FILE): return None
    try:
        with open(CREDENTIALS_FILE, 'r') as f: data=json.load(f); return data.get('username')
    except(json.JSONDecodeError,IOError) as e: print(f"{C_WARNING}{E_WARNING} Error reading {CREDENTIALS_FILE}: {e}{C_RESET}"); return None

def save_username(username):
    try:
        with open(CREDENTIALS_FILE, 'w') as f: json.dump({'username': username}, f)
        print(f"{C_INFO}{E_SAVE} Username '{username}' saved for next time.{C_RESET}")
    except IOError as e: print(f"{C_ERROR}{E_ERROR} Could not save username to {CREDENTIALS_FILE}: {e}{C_RESET}")

# === Selenium Login ===
def login_and_extract_selenium(url, username, password, output_filename=SELENIUM_OUTPUT_FILE):
    if not SELENIUM_AVAILABLE: print(f"{C_ERROR}{E_ERROR} Selenium unavailable.{C_RESET}"); return None,None
    driver=None; jsessionid=None
    start_loading(f"{E_GEAR} Initializing WebDriver...")
    try:
        opts=webdriver.ChromeOptions(); opts.add_argument('--headless'); opts.add_argument('--disable-gpu'); opts.add_argument('--log-level=3')
        opts.add_experimental_option('excludeSwitches',['enable-logging']); opts.add_argument("--window-size=1920,1080"); opts.add_argument("--no-sandbox"); opts.add_argument("--disable-dev-shm-usage")
        try:
            from webdriver_manager.chrome import ChromeDriverManager; from selenium.webdriver.chrome.service import Service as ChromeService
            os.environ['WDM_LOG_LEVEL']='0'; os.environ['WDM_PRINT_FIRST_LINE']='False'
            svc=ChromeService(ChromeDriverManager().install()); driver=webdriver.Chrome(service=svc,options=opts)
        except ImportError: stop_loading(); print(f"{C_WARNING}{E_WARNING} webdriver-manager missing. (pip install webdriver-manager)"); start_loading(f"{E_GEAR} Init WebDriver Fallback..."); driver=webdriver.Chrome(options=opts)
        except Exception as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} ChromeDriver setup failed: {e}{C_RESET}"); return None,None
        stop_loading(f"{E_COMPUTER} WebDriver Initialized.")
        print(f"{C_INFO}{E_LOGIN} Logging into: {C_CYAN}{url}{C_RESET}")
        start_loading(f"{E_EYES} Opening page..."); driver.get(url); stop_loading()
        uname_field=WebDriverWait(driver,15).until(EC.presence_of_element_located((By.NAME,"j_username"))); uname_field.clear(); uname_field.send_keys(username)
        pword_field=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME,"j_password"))); pword_field.clear(); pword_field.send_keys(password); print(f"{C_INFO}   Credentials entered.")
        login_btn=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button[type='submit']"))); start_loading(f"{E_ROCKET} Submitting..."); login_btn.click()
        try:
            WebDriverWait(driver,30).until(EC.any_of(
                EC.presence_of_element_located((By.ID,"logo")),
                EC.presence_of_element_located((By.ID,"hdWelcomeName")),
                EC.url_contains("Dashboard"),
                EC.presence_of_element_located((By.LINK_TEXT,"Logout")),
                EC.presence_of_element_located((By.XPATH,"//*[contains(text(), 'Welcome')]"))
            ))
            stop_loading(f"{E_SUCCESS} Login submitted, page loaded.")
        except TimeoutException:
            stop_loading()
            print(f"{C_WARNING}{E_WARNING} Post-login confirmation timeout.")
        
        pg_src = driver.page_source
        with open(output_filename,"w",encoding="utf-8") as f:
            f.write(pg_src)
        print(f"{C_DIM}   HTML saved to {output_filename}{C_RESET}")
        cookies=driver.get_cookies();
        for c in cookies:
            if c['name']=='JSESSIONID': jsessionid=c['value']; break
        if jsessionid: print(f"{C_SUCCESS}{E_SUCCESS} JSESSIONID obtained.")
        else: print(f"{C_ERROR}{E_ERROR} JSESSIONID NOT found. Login FAILED.")
    except(TimeoutException,WebDriverException,Exception)as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} Selenium Error: {e}{C_RESET}"); jsessionid = None # Ensure jsessionid is None on error
    finally:
        if driver: start_loading(f"{E_LOGOUT} Closing..."); driver.quit(); stop_loading(f"{E_LOGOUT} Closed.")
    return username if jsessionid else None, jsessionid # Return the initiating username if successful (JSESSIONID found)

# === Attendance Data Fetching ===
def fetch_attendance_data(jsessionid):
    if not jsessionid: print(f"{C_ERROR}{E_ERROR} JSESSIONID required.{C_RESET}"); return None
    cookies={'JSESSIONID':jsessionid}
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0','Accept':'application/json, text/javascript, */*; q=0.01','Accept-Language':'en-US,en;q=0.5','X-Requested-With':'XMLHttpRequest','Connection':'keep-alive','Referer':'https://nietcloud.niet.co.in/studentCourseFileNew.htm?shwA=%2700A%27','Sec-Fetch-Dest':'empty','Sec-Fetch-Mode':'cors','Sec-Fetch-Site':'same-origin',}
    params={'termId':'2','refreshData':'0'}
    url=NIET_ATTENDANCE_URL; print(f"\n{C_INFO}{E_ROCKET} Fetching attendance data...{C_RESET}")
    start_loading("Requesting from NIET Cloud..."); data,response=None,None
    try:
        response=requests.get(url,params=params,cookies=cookies,headers=headers,timeout=30)
        stop_loading(); response.raise_for_status(); data=response.json()
        with open(ATTENDANCE_FILE,'w') as f: json.dump(data,f,indent=4)
        print(f"{C_SUCCESS}{E_SUCCESS} Data saved to '{ATTENDANCE_FILE}'.{C_RESET}")
    except requests.exceptions.Timeout: stop_loading(); print(f"{C_ERROR}{E_ERROR} Request timed out.{C_RESET}")
    except requests.exceptions.HTTPError as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} HTTP Error: {e}{C_RESET}"); print(f"{C_DIM}Maybe expired JSESSIONID? Response:{response.text[:100] if response else 'N/A'}{C_RESET}")
    except requests.exceptions.RequestException as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} Network Error: {e}{C_RESET}")
    except json.JSONDecodeError: stop_loading(); print(f"{C_ERROR}{E_ERROR} Invalid JSON received.{C_RESET}"); print(f"{C_DIM}Response:{response.text[:100] if response else 'N/A'}{C_RESET}")
    except Exception as e: stop_loading(); print(f"{C_ERROR}{E_ERROR} Fetching error: {e}{C_RESET}")
    return data

# === Data Loading / Processing / Display (Keep stylish versions) ===
def load_attendance_data(json_file=ATTENDANCE_FILE):
    try:
        with open(json_file,'r') as f: print(f"{C_INFO}{E_INFO} Loading data from '{C_CYAN}{json_file}{C_INFO}'...{C_RESET}"); return json.load(f)
    except FileNotFoundError: print(f"{C_ERROR}{E_ERROR} File not found: '{json_file}'.{C_RESET}"); return None
    except json.JSONDecodeError: print(f"{C_ERROR}{E_ERROR} Invalid JSON in '{json_file}'.{C_RESET}"); return None
    except Exception as e: print(f"{C_ERROR}{E_ERROR} Error loading {json_file}: {e}{C_RESET}"); return None

def extract_summary_data(data):
    if not isinstance(data,list): print(f"{C_ERROR}{E_ERROR} Invalid data.{C_RESET}"); return [],0,0
    summary=[]; total_p=0; total_c=0
    for sub in data:
        if not isinstance(sub,dict): continue
        p=int(sub.get('presentCount',0)); a=int(sub.get('absentCount',0)); t=p+a; perc=(p/t*100)if t>0 else 0; perc_s=f"{perc:.2f}%"
        if t>0: c,e=(C_LOW,E_SAD) if perc<75 else (C_MID,E_NEUTRAL) if perc<85 else (C_HIGH,E_HAPPY); perc_d=f"{c}{C_BOLD}{perc_s}{C_RESET} {e}"
        else: perc_d=f"{C_DIM}{perc_s} N/A{C_RESET}"
        summary.append({'Code':f"{C_DIM}{sub.get('subjectCode','N/A')}{C_RESET}",f'{E_BOOK} Course':f"{C_SUBJECT}{sub.get('subject','N/A')}{C_RESET}",'Count':f"{p}/{t}",f'{E_CHART_UP} %':perc_d})
        total_p+=p; total_c+=t
    ov_perc=(total_p/total_c*100)if total_c>0 else 0
    if total_c>0: c,e=(C_LOW,E_SAD) if ov_perc<75 else (C_MID,E_NEUTRAL) if ov_perc<85 else (C_HIGH,E_HAPPY); ov_perc_d=f"{c}{C_BOLD}{ov_perc:.2f}%{C_RESET} {e}"
    else: ov_perc_d=f"{C_DIM}{ov_perc:.2f}% N/A{C_RESET}"
    summary.append({'Code':'',f'{E_BOOK} Course':f'{C_WHITE}{C_BOLD}TOTAL{C_RESET}', 'Count':f"{C_WHITE}{C_BOLD}{total_p}/{total_c}{C_RESET}", f'{E_CHART_UP} %':ov_perc_d})
    return summary,total_p,total_c

def extract_detailed_attendance(sub_data):
    details=[]; p_entries=[]
    att_str = sub_data.get('studentAttendanceData','');
    if not att_str: return details
    for entry in att_str.split(';'):
        if not entry: continue
        parts=entry.split('^^^');
        if len(parts)>=6:
            d_s,s_t,e_t,st,sess,_=parts[:6]
            try:
                d_o=datetime.strptime(d_s.strip(),'%b %d, %Y'); st_l=st.lower(); st_d=f"{C_GREEN}Present{C_RESET} 👍" if st_l=='present' else f"{C_RED}Absent{C_RESET}  👎" if st_l=='absent' else st
                p_entries.append({'d_o':d_o,'Sr':0,f'{E_CALENDAR} Date':d_o.strftime('%b %d, %Y'),f'{E_CLOCK} Time':f"{s_t}-{e_t}",'Session':sess,'Status':st_d})
            except ValueError: continue
    p_entries.sort(key=lambda x:x['d_o'],reverse=True)
    for i,item in enumerate(p_entries,1): item['Sr']=f"{C_DIM}{i}{C_RESET}"; del item['d_o']; details.append(item)
    return details

def display_summary(summary_data):
    if not summary_data: print(f"{C_WARNING}{E_WARNING} No summary data.{C_RESET}"); return
    try:
        df=pd.DataFrame(summary_data); print(f"\n{C_HEADER}{E_STAR}=== Attendance Summary ==={E_STAR}{C_RESET}\n")
        print(tabulate(df,headers='keys',tablefmt='fancy_grid',showindex=False))
    except Exception as e: print(f"{C_ERROR}{E_ERROR} Error displaying summary: {e}{C_RESET}")

def display_subject_details(subject,details_data):
    if not details_data: print(f"\n{C_WARNING}{E_WARNING} No details for {subject}.{C_RESET}"); return
    try:
        df=pd.DataFrame(details_data); subj_d=f"{C_SUBJECT}{C_BOLD}{subject}{C_RESET}"
        print(f"\n{C_HEADER}=== {E_EYES} Details: {subj_d} ==={C_RESET}\n"); print(tabulate(df,headers='keys',tablefmt='fancy_grid',showindex=False))
    except Exception as e: print(f"{C_ERROR}{E_ERROR} Error displaying details: {e}{C_RESET}")

# === Calculations (Keep previous robust versions) ===
def calculate_classes_needed_for_target(total_present, total_classes, target_percentage=85):
    if total_classes<=0: return 0,0,0.0
    curr_p=(total_present/total_classes*100);
    if curr_p>=target_percentage: return 0,0,curr_p
    if target_percentage>=100 and total_present<total_classes: return float('inf'),float('inf'),curr_p
    num=(target_percentage*total_classes-100*total_present); den=(100-target_percentage)
    if den<=0: return float('inf'),float('inf'),curr_p
    cls_n=math.ceil(num/den);
    if cls_n<0: cls_n=0
    days_n=0; cls_rem=cls_n; curr_d=date.today()
    while cls_rem>0:
        if days_n>730: days_n=float('inf'); break
        days_n+=1; curr_d+=timedelta(days=1); dow=curr_d.weekday(); cls_tdy=7 if dow<5 else 6 if dow==5 else 0
        cls_rem-=min(cls_tdy,cls_rem)
    new_p=total_present+cls_n; new_c=total_classes+cls_n; new_perc=(new_p/new_c*100) if new_c>0 else 0
    return cls_n,days_n,new_perc

def calculate_leave_allowance(total_present, total_classes, target_percentage=85):
    if total_classes<=0: return {'current_percentage':0.0,'target_percentage':target_percentage,'max_absences':0,'detailed_days_leave':0,'can_maintain_target':False}
    curr_p=(total_present/total_classes*100);
    if target_percentage<=0: return {'current_percentage':curr_p,'target_percentage':target_percentage,'max_absences':float('inf'),'detailed_days_leave':float('inf'),'can_maintain_target':True}
    if curr_p<target_percentage: max_abs=-1; can_m=False
    else: max_abs=math.floor((total_present*100/target_percentage)-total_classes); can_m=True
    if max_abs<0: max_abs=0
    days_l=0; abs_rem=max_abs; curr_idx=date.today().weekday()
    while abs_rem>0:
        if days_l>730: days_l=float('inf'); break
        cls_tdy=7 if curr_idx<5 else 6 if curr_idx==5 else 0
        if cls_tdy>0: miss_tdy=min(cls_tdy,abs_rem);
        if miss_tdy>0: days_l+=1; abs_rem-=miss_tdy
        curr_idx=(curr_idx+1)%7
    return {'current_percentage':curr_p,'target_percentage':target_percentage,'max_absences':max_abs,'detailed_days_leave':days_l,'can_maintain_target':can_m}

def calculate_future_attendance(total_present, total_classes, end_date_str, holidays=None):
    hols=set(holidays) if holidays else set()
    try:
        end_d=datetime.strptime(end_date_str,"%Y-%m-%d").date(); curr_d=date.today()
        if curr_d>=end_d: return {'error':'End date must be future.'}
        fut_cls=0; fut_days_sched=[]; temp_d=curr_d
        while temp_d<end_d:
            temp_d+=timedelta(days=1); date_s=temp_d.strftime("%Y-%m-%d")
            if date_s in hols: fut_days_sched.append((temp_d,0)); continue
            dow=temp_d.weekday(); cls_day= 7 if dow<5 else 6 if dow==5 else 0
            fut_days_sched.append((temp_d,cls_day));
            if cls_day>0: fut_cls+=cls_day
        fut_tot_cls=total_classes+fut_cls; curr_p=(total_present/total_classes*100) if total_classes>0 else 0.0
        cls_needed_85=0; proj_all_p=total_present+fut_cls; proj_perc_all=(proj_all_p/fut_tot_cls*100) if fut_tot_cls>0 else 0.0
        if proj_perc_all<85: req_fut_p=math.ceil(0.85*fut_tot_cls-total_present); cls_needed_85=max(0,req_fut_p);
        if cls_needed_85>fut_cls: cls_needed_85=float('inf')
        scenarios=[]; percs_check=[100,95,90,85,75,50,0]
        for fut_att_p in percs_check:
            if fut_cls==0: fut_p=0; days_4_cls=0
            else:
                fut_p=math.floor(fut_cls*(fut_att_p/100.0)); days_4_cls=0; cls_2att_cnt=fut_p
                for day_d,day_c in fut_days_sched:
                    if cls_2att_cnt<=0: break
                    if day_c>0: att_tdy=min(day_c,cls_2att_cnt);
                    if att_tdy>0: days_4_cls+=1; cls_2att_cnt-=att_tdy
            proj_tot_p=total_present+fut_p; proj_p=(proj_tot_p/fut_tot_cls*100) if fut_tot_cls>0 else 0.0
            scenarios.append({'future_attendance':fut_att_p,'classes_to_attend':fut_p,'days_to_attend':days_4_cls,'projected_total':f"{proj_tot_p}/{fut_tot_cls}",'projected_percentage':round(proj_p,2)})
        return {'current_total':f"{total_present}/{total_classes}",'current_percentage':round(curr_p,2),'future_classes':fut_cls,'future_total_classes':fut_tot_cls,'classes_needed_85':cls_needed_85,'scenarios':scenarios}
    except ValueError: return{'error':'Invalid date format YYYY-MM-DD.'}
    except Exception as e: return {'error':f'Future calc error: {e}'}

# === Calculation Display (Keep stylish versions) ===
def display_leave_allowance_results(result, total_p, total_c):
    print(f"\n{C_HEADER}{E_TARGET}=== Leave Allowance Calculator ==={C_RESET}\n")
    print(f"Current Attendance: {result['current_percentage']:.2f}%"); print(f"Target Attendance:  {result['target_percentage']:.2f}%")
    if result['can_maintain_target']:
        if result['max_absences']==0: print(f"\n{C_YELLOW}{E_NEUTRAL} Exactly at target. Cannot miss more.{C_RESET}")
        else: print(f"\n{C_GREEN}{E_HAPPY} Can miss up to {C_BOLD}{result['max_absences']}{C_RESET}{C_GREEN} classes (stay >= {result['target_percentage']}%).{C_RESET}"); print(f"{C_GREEN}   Approx. {C_BOLD}{result['detailed_days_leave']}{C_RESET}{C_GREEN} leave days.{C_RESET}")
    else:
        print(f"\n{C_WARNING}{E_SAD} Below target.{C_RESET}")
        cls_n,days_n,new_p = calculate_classes_needed_for_target(total_p,total_c,result['target_percentage'])
        if cls_n==float('inf'): print(f"{C_ERROR}{E_ERROR} Impossible to reach {result['target_percentage']}%{C_RESET}")
        else: print(f"{C_YELLOW}{E_POINT_RIGHT} Need {C_BOLD}{cls_n}{C_RESET}{C_YELLOW} consecutive classes ({result['target_percentage']}%)"); print(f"{C_YELLOW}   Approx. {C_BOLD}{days_n}{C_RESET}{C_YELLOW} school days."); print(f"{C_YELLOW}   New attendance ~{C_BOLD}{new_p:.2f}%{C_RESET}{C_YELLOW}.{C_RESET}")

def display_future_attendance_results(result):
    if 'error' in result: print(f"\n{C_ERROR}{E_ERROR} {result['error']}{C_RESET}"); return
    print(f"\n{C_HEADER}{E_CALENDAR}=== Future Attendance Projection ==={C_RESET}\n")
    print(f"Current: {result['current_total']} ({result['current_percentage']}%)"); print(f"Future Classes: {result['future_classes']}"); print(f"Total by End Date: {result['future_total_classes']}")
    if result['classes_needed_85'] != 0:
        if result['classes_needed_85']==float('inf'): print(f"\n{C_ERROR}{E_CHART_DOWN} Impossible to reach 85% by date.{C_RESET}")
        elif result['classes_needed_85']>0: print(f"\n{C_YELLOW}{E_TARGET} For 85%, must attend {C_BOLD}{result['classes_needed_85']}{C_RESET}{C_YELLOW}/{result['future_classes']} future classes.{C_RESET}")
    print(f"\n{C_BLUE}{E_THINK} Projections based on future attendance:{C_RESET}")
    scen_data=[]
    for s in result['scenarios']:
         proj_p=s['projected_percentage']; c,e= (C_LOW,E_SAD) if proj_p<75 else (C_MID,E_NEUTRAL) if proj_p<85 else (C_HIGH,E_HAPPY); clr_p=f"{c}{C_BOLD}{proj_p:.2f}%{C_RESET} {e}"
         scen_data.append({f'{E_ROCKET}Future Attend %':f"{s['future_attendance']}%",'Classes':s['classes_to_attend'],'Days Req.':s['days_to_attend'],'Proj.Total':s['projected_total'], f'{E_CHART_UP}Proj.Overall %':clr_p})
    try: df=pd.DataFrame(scen_data); print(tabulate(df,headers='keys',tablefmt='fancy_grid',showindex=False))
    except Exception as e: print(f"{C_ERROR}{E_ERROR} Proj table error: {e}{C_RESET}")


# === Main Loop (Keep stylish versions) ===
def run_attendance_tracker(attendance_data):
    if not attendance_data: print(f"{C_WARNING}{E_WARNING} No data.{C_RESET}"); return
    summary,total_p,total_c = extract_summary_data(attendance_data)
    if not summary: print(f"{C_ERROR}{E_ERROR} Summary extraction failed.{C_RESET}"); return
    display_summary(summary)
    if total_c>0:
        curr_p=(total_p/total_c*100)
        if curr_p<85:
            cls_n,days_n,_=calculate_classes_needed_for_target(total_p,total_c,85)
            bdr=f"{C_RED}{'='*20} {E_WARNING} ALERT {E_WARNING} {'='*20}{C_RESET}"
            print("\n"+bdr); print(f"{C_WARNING}Overall attendance ({C_BOLD}{curr_p:.2f}%{C_RESET}{C_WARNING}) < 85%! {E_SAD}{C_RESET}")
            if cls_n!=float('inf'): print(f"{C_YELLOW}{E_POINT_RIGHT} Need {C_BOLD}{cls_n}{C_RESET}{C_YELLOW} consecutive classes."); print(f"{C_YELLOW}   Approx. {C_BOLD}{days_n}{C_RESET}{C_YELLOW} school days.{C_RESET}")
            else: print(f"{C_ERROR}{E_ERROR} Impossible to reach 85%.{C_RESET}")
            print(f"{C_RED}{'='*len(bdr.replace(C_RED,'').replace(C_RESET,'').replace(E_WARNING,' '))}{C_RESET}")
    while True:
        print(f"\n{C_HEADER}--- {E_GEAR} Options Menu ---{C_RESET}"); print(f"  {C_CYAN}1{C_RESET}. {E_EYES} Detailed Attendance"); print(f"  {C_CYAN}2{C_RESET}. {E_TARGET} Leave Allowance (85%)"); print(f"  {C_CYAN}3{C_RESET}. {E_CALENDAR} Future Projection"); print(f"  {C_CYAN}4{C_RESET}. {E_CHART_UP} Custom Target %"); print(f"  {C_CYAN}0{C_RESET}. {E_LOGOUT} Exit")
        try:
            ch_s=input(f"\n{C_PROMPT} Choice: {C_RESET}").strip()
            if not ch_s.isdigit(): print(f"{C_WARNING}{E_WARNING} Invalid input.{C_RESET}"); continue
            ch=int(ch_s); print("-" * 40)
            if ch==0: print(f"{C_INFO}{E_WAVE} Exiting.{C_RESET}"); break
            elif ch==1:
                 sub_list=[]; print(f"{C_BLUE}{E_BOOK} Select Subject:{C_RESET}")
                 for i,sub in enumerate(attendance_data,1):
                     if isinstance(sub, dict): s_n=sub.get('subject','N/A'); s_c=sub.get('subjectCode','N/A'); sub_list.append((i,s_n,s_c)); print(f"  {C_CYAN}{i}{C_RESET}. {s_n} [{C_DIM}{s_c}{C_RESET}]")
                 if not sub_list: print(f"{C_WARNING}No subjects.{C_RESET}"); continue
                 try:
                     sub_ch_s=input(f"\n{C_PROMPT} Subject number: {C_RESET}").strip()
                     if not sub_ch_s.isdigit(): print(f"{C_WARNING}Invalid #.{C_RESET}"); continue
                     sub_ch=int(sub_ch_s)
                     if 1<=sub_ch<=len(sub_list):
                         sel_idx=sub_ch-1
                         if isinstance(attendance_data[sel_idx], dict): details=extract_detailed_attendance(attendance_data[sel_idx]); display_subject_details(sub_list[sel_idx][1], details)
                         else: print(f"{C_ERROR}Bad data struct.{C_RESET}")
                     else: print(f"{C_WARNING}Invalid choice.{C_RESET}")
                 except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
            elif ch==2: result=calculate_leave_allowance(total_p,total_c,85); display_leave_allowance_results(result, total_p, total_c)
            elif ch==3:
                while True:
                     ed_s=input(f"{C_PROMPT}{E_CALENDAR} End date (YYYY-MM-DD): {C_RESET}").strip()
                     try: datetime.strptime(ed_s,"%Y-%m-%d"); break
                     except ValueError: print(f"{C_WARNING}Invalid format.{C_RESET}")
                hols=[]; add_h=input(f"{C_PROMPT}Add holidays? (y/n): {C_RESET}").lower().strip()
                if add_h=='y':
                    print(f"{C_DIM}Enter holiday dates (YYYY-MM-DD), blank line when done.{C_RESET}")
                    while True:
                        h=input(f"{C_PROMPT} Holiday date: {C_RESET}").strip()
                        if not h: break
                        try: datetime.strptime(h,"%Y-%m-%d"); hols.append(h)
                        except ValueError: print(f"{C_WARNING}Invalid date format.{C_RESET}")
                result=calculate_future_attendance(total_p,total_c,ed_s,hols); display_future_attendance_results(result)
            elif ch==4:
                while True:
                    t_s = input(f"{C_PROMPT}{E_TARGET} Target %: {C_RESET}").strip()
                    try:
                        t = float(t_s)
                        if 0 < t <= 100:
                            break
                        else:
                            print(f"{C_WARNING}Target 0-100 only.{C_RESET}")
                    except ValueError:
                        print(f"{C_WARNING}Invalid number.{C_RESET}")
                cls_n, days_n, new_p = calculate_classes_needed_for_target(total_p,total_c,t)
                hdr=f" Reaching {t}% Attendance "; print(f"\n{C_HEADER}---{hdr}---{C_RESET}")
                if cls_n==float('inf'): print(f"{C_ERROR}{E_ERROR} Impossible to reach {t}%{C_RESET}")
                else: print(f"{C_YELLOW}{E_POINT_RIGHT} Need {C_BOLD}{cls_n}{C_RESET}{C_YELLOW} consecutive classes."); print(f"{C_YELLOW}   Approx. {C_BOLD}{days_n}{C_RESET}{C_YELLOW} school days."); print(f"{C_YELLOW}   New attendance ~{C_BOLD}{new_p:.2f}%{C_RESET}{C_YELLOW}.{C_RESET}")
                print(f"{C_HEADER}{'-'*(len(hdr)+6)}{C_RESET}")
            else: print(f"{C_WARNING}{E_WARNING} Invalid choice.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
        except KeyboardInterrupt: print(f"\n{C_YELLOW}{E_WARNING} Operation interrupted.{C_RESET}"); continue


# === Main Orchestration ===
def main():
    clear_screen()
    print(f"{C_TITLE}{C_BOLD}{'*'*40}{C_RESET}")
    print(f"{C_TITLE}{C_BOLD}*    📊 NIET Attendance Tracker {E_ROCKET}    *{C_RESET}")
    print(f"{C_TITLE}{C_BOLD}{'*'*40}{C_RESET}")
    if not TABULATE_AVAILABLE: print(f"{C_WARNING}{E_WARNING} 'tabulate' missing. Tables will be basic CSV format. (pip install tabulate)")

    att_data=None; jsessionid=None; last_username=load_saved_username()

    options=[(f"{E_COMPUTER}Log in via Browser",SELENIUM_AVAILABLE,1), (f"{E_LOGIN}Use existing JSESSIONID",True,2), (f"{E_BOOK}Load from '{ATTENDANCE_FILE}'",True,3)]
    print(f"\n{C_BLUE}{E_POINT_RIGHT} How to get data?{C_RESET}")
    for i,(text,enabled,_) in enumerate(options,1): print(f"  {C_CYAN}{i}{C_RESET}. {text}" if enabled else f"  {C_DIM}{i}. {text} (Disabled){C_RESET}")

    while True:
        try:
            ch_s=input(f"\n{C_PROMPT} Choice: {C_RESET}").strip(); choice=int(ch_s)
            if 1<=choice<=len(options):
                 if not options[choice-1][1]: print(f"{C_ERROR}{E_ERROR} Option disabled.{C_RESET}"); continue
                 break
            else: print(f"{C_WARNING}Invalid choice #.{C_RESET}")
        except ValueError: print(f"{C_WARNING}Invalid number.{C_RESET}")
        except KeyboardInterrupt: print("\nExiting."); sys.exit(0)

    print("-" * 40); choice_num=options[choice-1][2] # Get choice number (1, 2, or 3)

    if choice_num==1: # Selenium Login
        print(f"{C_HEADER}--- {E_LOGIN} Selenium Login ---{C_RESET}")
        username_to_use=None
        if last_username:
            use_saved=input(f"{C_PROMPT}{E_REUSE} Use saved username '{C_CYAN}{last_username}{C_PROMPT}'? (Y/n): {C_RESET}").strip().lower()
            if use_saved=='' or use_saved=='y': username_to_use=last_username; print(f"{C_INFO}{E_WAVE} Using saved username: {username_to_use}{C_RESET}")
            else: last_username=None # Clear if not used
        if not username_to_use: username_to_use=input(f"{C_PROMPT} NIET Cloud username: {C_RESET}").strip()
        if not username_to_use: print(f"{C_ERROR}Username required. Exiting."); sys.exit(1) # Exit if no username provided

        password = getpass.getpass(f"{C_PROMPT} NIET Cloud password: {C_RESET}")
        if not password: print(f"{C_ERROR}Password required. Exiting."); sys.exit(1) # Exit if no password provided

        login_username, jsessionid = login_and_extract_selenium(NIET_LOGIN_URL, username_to_use, password)

        if jsessionid and login_username: # Check if login was successful AND username confirmed by function return
             # Only ask to save if login worked AND we weren't already using the saved one OR the saved one was different
             if last_username != login_username:
                 save_choice = input(f"{C_PROMPT}{E_SAVE} Save username '{C_CYAN}{login_username}{C_PROMPT}' for next time? (Y/n): {C_RESET}").strip().lower()
                 if save_choice=='' or save_choice=='y': save_username(login_username)

             att_data=fetch_attendance_data(jsessionid)
             if not att_data: print(f"\n{C_WARNING}{E_WARNING} Fetch failed after login. Trying local file...{C_RESET}"); att_data = load_attendance_data()
        else:
             print(f"{C_ERROR}{E_ERROR} Login failed. Cannot fetch fresh data.{C_RESET}")
             fallback=input(f"{C_PROMPT}Try loading from '{ATTENDANCE_FILE}'? (y/n): {C_RESET}").lower()
             if fallback=='y': att_data=load_attendance_data()

    elif choice_num==2: # Existing JSESSIONID
        print(f"{C_HEADER}--- {E_LOGIN} Use Existing JSESSIONID ---{C_RESET}")
        jsessionid=input(f"{C_PROMPT} Enter JSESSIONID: {C_RESET}").strip()
        if jsessionid:
            att_data = fetch_attendance_data(jsessionid)
            if not att_data: print(f"\n{C_WARNING}{E_WARNING} Fetch failed. Trying local file...{C_RESET}"); att_data = load_attendance_data()
        else: print(f"{C_WARNING}No JSESSIONID. Trying local file...{C_RESET}"); att_data = load_attendance_data()

    elif choice_num==3: # Load from file
        print(f"{C_HEADER}--- {E_BOOK} Load from File ---{C_RESET}")
        f_path=input(f"{C_PROMPT} File path (Enter for '{ATTENDANCE_FILE}'): {C_RESET}").strip()
        att_data=load_attendance_data(f_path if f_path else ATTENDANCE_FILE)

    # --- Run tracker ---
    if att_data:
        try: run_attendance_tracker(att_data)
        except KeyboardInterrupt: print(f"\n{C_YELLOW}Exiting.{C_RESET}")
        except Exception as e: print(f"\n{C_ERROR}{E_ERROR} Tracker Error: {e}{C_RESET}"); import traceback; print(f"{C_DIM}{traceback.format_exc()}{C_RESET}")
    else: print(f"\n{C_ERROR}{E_ERROR} Failed to get attendance data. Cannot proceed.{C_RESET}"); sys.exit(1)

if __name__ == "__main__":
    main()
