# 🎓✅ NIET Attendance Tracker

A Python-based tool 🐍 for tracking and analyzing attendance data 📊 from the NIET student portal. This tool provides a user-friendly interface 💻 to view attendance records, calculate leave allowances, and project future attendance scenarios 🚀.

## 🚀 Installation

### For Windows Users 🪟

1.  **Install Python** 🐍 (if not already installed):

    *   **Using winget** ⚙️:
        *(Run this in your Terminal, like PowerShell or Command Prompt)*
        ```powershell
        winget install -e --id Python.Python.3.11
        ```

    *   Verify installation by opening **Terminal** and typing:

        ```powershell
        python --version
        ```

2.  **Set Script Execution Policy (Windows - PowerShell Recommended)** 🛡️:
    *(This allows running local scripts. Open PowerShell as Administrator)*
    ```powershell
    Set-ExecutionPolicy Unrestricted
    ```
    Type 'A' when prompted to accept all changes. *(You can change this back later if desired with `Set-ExecutionPolicy Restricted`)*

3.  **Download the Script** ⬇️:
    *(Run this in your Terminal)*
    ```powershell
    curl -o niet_attendance_tracker_windows.py https://raw.githubusercontent.com/iamawanishmaurya/NIET-Attendance-Tracker/refs/heads/main/niet_attendance_tracker_windows.py
    ```
4.  Run the script in your **Terminal**:
    ```powershell
    python niet_attendance_tracker_windows.py
    ```


### For Linux Users 🐧

1.  **Install Prerequisites** (Python 3, pip, venv):
    *(Open your Terminal)*

    *   **Debian/Ubuntu:**
        ```bash
        sudo apt update && sudo apt install python3 python3-pip python3-venv -y
        ```
    *   **Fedora:**
        ```bash
        sudo dnf install python3 python3-pip -y
        ```
    *   **Arch Linux:**
        ```bash
        sudo pacman -Syu python python-pip --noconfirm
        ```
    *   Verify installation:
        ```bash
        python3 --version
        pip3 --version
        ```

2.  **Download the Script** ⬇️:
    *(Run this in your Terminal)*
    ```bash
    curl -o niet_attendance_tracker.py https://raw.githubusercontent.com/iamawanishmaurya/NIET-Attendance-Tracker/refs/heads/main/niet_attendance_linux.py
    ```

3.  **Set up a Virtual Environment** (Recommended)  izoláláshoz:
    *(In the same directory where you downloaded the script)*
    ```bash
    python3 -m venv niet_env
    source niet_env/bin/activate
    ```
    *(You should see `(niet_env)` at the beginning of your terminal prompt)*

4.  **Install Dependencies** 📦:
    *(Make sure your virtual environment is active)*
    ```bash
    pip install requests pandas cryptography rich tabulate selenium webdriver-manager colorama beautifulsoup4
    ```
    *   **Note:** `rich`, `tabulate`, and `cryptography` enhance the experience but the script has fallbacks if they are missing. `cryptography` is needed for saving passwords securely.

5.  **Install Web Browsers & Drivers** 🌐:
    *   Ensure you have **Firefox**, **Google Chrome**, or **Microsoft Edge** installed.
    *   The script uses `webdriver-manager` to automatically download the correct browser drivers (like `geckodriver` or `chromedriver`). If this fails (e.g., due to network issues), you might need to install the driver manually and ensure it's in your system's PATH.

6.  **Run the Script**:
    *(Make sure your virtual environment is active)*
    ```bash
    python3 niet_attendance_tracker_linux.py
    ```

7.  **Set up Alias (Optional)** ⚡:
    *   To run the script simply by typing `niet`, first run the setup command:
        ```bash
        python3 niet_attendance_tracker_linux.py --setup-alias
        ```
    *   Follow the prompts. You will need to **restart your terminal** or run `source ~/.bashrc` (or `source ~/.zshrc` if you use zsh) for the alias to take effect.
    *   After setup, you can run the tracker using:
        ```bash
        niet
        ```

## 📸 Screenshots

<table>
  <tr>
    <td align="center" width="33%">
        <img src="assests/gif/installation.gif" width="100%" alt="Installation"/>
        <br/><sub>Linux Installation Demo</sub>
    </td>
    <td align="center" width="33%">
        <img src="assests/images/Niet_Attendance_Tracker.jpg" width="100%" alt="NIET Attendance Tracker"/>
        <br/><sub>Main Menu</sub>
    </td>
    <td align="center" width="33%">
        <img src="assests/images/Attendance_Summary.jpg" width="100%" alt="Attendance Summary"/>
        <br/><sub>Attendance Summary (Rich)</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
        <img src="assests/images/Detailed_Attendance.jpg" width="100%" alt="Detailed Attendance"/>
        <br/><sub>Detailed View (Rich)</sub>
    </td>
    <td align="center" width="33%">
        <img src="assests/images/Future_Attendance_Projection.jpg" width="100%" alt="Future Attendance Projection"/>
        <br/><sub>Future Projection (Rich)</sub>
    </td>
     <td align="center" width="33%">
        <img src="assests/images/leave_allowance.jpg" width="100%" alt="Leave Allowance"/>
        <br/><sub>Leave Allowance Calc</sub>
    </td>
  </tr>
</table>

## ✨ Features

-   🔐 **Secure Credential Management**
    -   Save and encrypt login credentials locally 💾 (requires `cryptography`)
    -   Manage multiple user profiles 🧑‍🤝‍🧑
    -   Secure password storage using Fernet encryption 🛡️
    -   Easy credential selection 🔄

-   🤖 **Automated Login (via Selenium)**
    -   Support for Firefox 🔥, Chrome 🌐, and Edge browsers.
    -   Automatic driver management via `webdriver-manager` ⚙️
    -   Session reuse possibility via JSESSIONID input 🍪
    -   SSL verification options ✅

-   📊 **Attendance Analysis**
    -   Clear subject-wise attendance summary 📈
    -   Detailed attendance records with dates & times 📅
    -   Color-coded attendance status 🎨 (🟢🟡🔴) using `rich` or `colorama`
    -   Overall attendance percentage calculation

-   🧮 **Projections & Calculations**
    -   **Leave Allowance:** Calculate how many classes can be missed while maintaining a target % 🏖️
    -   **Target Achievement:** Calculate classes needed to reach a specific target % 🎯
    -   **Future Projection:** Estimate attendance by a future date based on different attendance rates 🔮
    -   Holiday consideration for future projections 🏝️

-   🎨 **User Interface**
    -   Enhanced terminal interface with colors and formatting (best with `rich`) 🌈
    -   Loading animations and progress indicators ⏳
    -   Formatted tables for readability (requires `rich` or `tabulate`) 📝
    -   Interactive command-line menus and prompts 👉

-   👥 **Dynamic Contributor Display**
    -   Fetches contributor list directly from GitHub 🤝
    -   Assigns unique colors and emojis to contributors ✨
    -   Visually acknowledges community contributions 🌟

## ▶️ Usage

1.  **Activate Environment (if using venv):**
    *   Linux: `source niet_env/bin/activate`
    *   Windows: `.\niet_env\Scripts\activate`

2.  **Run the script:**
    *   If alias is set up (Linux): `niet`
    *   Otherwise: `python3 niet_attendance_tracker.py` (Linux) or `python niet_attendance_tracker.py` (Windows)

3.  **Follow On-Screen Prompts:**
    *   Choose your preferred browser (if logging in).
    *   Select login method: Browser Login, Use existing JSESSIONID, or Load from file.
    *   If Browser Login: Select saved credentials or enter new ones.
    *   Once data is loaded, use the menu options:
        *   `1`: View Detailed Attendance (per subject) 👀
        *   `2`: Calculate Leave Allowance (for 85%) 🏖️
        *   `3`: Project Future Attendance (custom date) 🔮
        *   `4`: Calculate Classes Needed (custom target %) 🎯
        *   `5`: View Overall Summary Again 📊
        *   `0`: Exit 👋

## 🛡️ Security Features

-   🔑 **Encrypted Credential Storage:** Passwords are encrypted using the `cryptography` library if installed and saved locally in `credentials.json`. The encryption key is stored separately in `secret.key`. **Keep `secret.key` safe and backed up! If lost, saved passwords cannot be recovered.**
-   🔒 **Secure Password Handling:** Passwords are masked during input using `getpass`.
-   🏠 **Local Data Storage:** All sensitive data (credentials, key, fetched attendance) is stored only on your local machine.
-   🚫 **No Data Transmission:** Your credentials and detailed attendance data are **not** sent to any third-party servers by this script (only to the official NIET portal during login/data fetch).
-   ✅ **SSL Verification:** Standard SSL certificate verification is used by default for requests. An option exists to bypass verification for troubleshooting, but use with caution.

## 🙏 Acknowledgments

-   Developed with input and testing from the NIET student community 🧑‍🎓.
-   Leverages fantastic open-source Python libraries ❤️.
-   Special thanks to all contributors!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/iamawanishmaurya/NIET-Attendance-Tracker/issues).

The project uses a dynamic contributor display system powered by `contrib.rocks`.

### Contributors 🧑‍💻

<a href="https://github.com/iamawanishmaurya/NIET-Attendance-Tracker/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=iamawanishmaurya/NIET-Attendance-Tracker" />
</a>

![Alt](https://repobeats.axiom.co/api/embed/fa3995e7339da9586497c625c8613579549e4d78.svg "Repobeats analytics image")

## ⭐ Star History

Show your support by starring the project!

<a href="https://star-history.com/#iamawanishmaurya/NIET-Attendance-Tracker&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=iamawanishmaurya/NIET-Attendance-Tracker&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=iamawanishmaurya/NIET-Attendance-Tracker&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=iamawanishmaurya/NIET-Attendance-Tracker&type=Date" />
 </picture>
</a>
