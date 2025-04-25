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

## 📸 Screenshots

<table>
  <tr>
    <td align="center" width="33%">
        <img src="assests/gif/installation.gif" width="100%" alt="Installation"/>
        <br/><sub>Installation Process</sub>
    </td>
    <td align="center" width="33%">
        <img src="assests/images/Niet_Attendance_Tracker.jpg" width="100%" alt="NIET Attendance Tracker"/>
        <br/><sub>Main Menu</sub>
    </td>
    <td align="center" width="33%">
        <img src="assests/images/Attendance_Summary.jpg" width="100%" alt="Attendance Summary"/>
        <br/><sub>Attendance Summary</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
        <img src="assests/images/Detailed_Attendance.jpg" width="100%" alt="Detailed Attendance"/>
        <br/><sub>Detailed View</sub>
    </td>
    <td align="center" width="33%">
        <img src="assests/images/Future_Attendance_Projection.jpg" width="100%" alt="Future Attendance Projection"/>
        <br/><sub>Future Projection</sub>
    </td>
     <td align="center" width="33%">
        <!-- Add another image here if you have one, or leave blank/adjust widths -->
    </td>
  </tr>
</table>

## ✨ Features

-   🔐 **Secure Credential Management**
    -   Save and encrypt login credentials locally 💾
    -   Manage multiple user profiles with aliases 🧑‍🤝‍🧑
    -   Secure password storage using cryptography 🛡️
    -   Easy credential switching between profiles 🔄

-   🤖 **Automated Login**
    -   Support for multiple browsers (Chrome 🌐, Firefox 🔥, Edge 엣지?)
    -   Automatic browser detection and setup ⚙️
    -   Session management with JSESSIONID 🍪
    -   SSL verification options ✅

-   📊 **Attendance Analysis**
    -   View subject-wise attendance summary 📈
    -   Detailed attendance records with dates 📅
    -   Color-coded attendance status 🎨 (🟢🟡🔴)
    -   Leave allowance calculation 🏖️
    -   Future attendance projections 🔮

-   🧮 **Advanced Calculations**
    -   Target-based attendance planning 🎯
    -   Leave allowance recommendations 👍
    -   Future attendance scenarios 🤔
    -   Holiday-aware calculations 🏝️

-   🎨 **User Interface**
    -   Rich terminal interface with colors 🌈
    -   Progress bars and loading animations ⏳
    -   Formatted tables and displays 📝
    -   Interactive menus and prompts 👉

-   👥 **Dynamic Contributor Display**
    -   Real-time GitHub contributor fetching 🤝
    -   Unique color and emoji combinations ✨
    -   Automatic style assignment for new contributors 🌟
    -   Visual hierarchy for different roles 👑

## ▶️ Usage

1.  Run the script in your **Terminal**:
    ```powershell
    niet
    ```

2.  Choose your login method:
    *   ✅ Use saved credentials
    *   🆕 Enter new credentials
    *   🍪 Use JSESSIONID

3.  Select your preferred browser (if not using saved session) 🌐

4.  View your attendance data and use the various analysis tools:
    *   👀 View attendance summary
    *   🗓️ Check detailed records
    *   🏖️ Calculate leave allowance
    *   🔮 Project future attendance

## 🛡️ Security Features

-   🔑 Encrypted credential storage
-   🔒 Secure password handling
-   🏠 Local data storage
-   🚫 No data transmission to external servers
-   ✅ SSL verification options

## 🙏 Acknowledgments

-   Enhanced by the NIET student community 🧑‍🎓
-   Special thanks to all contributors who have helped improve this tool ❤️

## 🤝 Contributing

Contributions are welcome! The project uses a dynamic contributor display system that automatically recognizes and styles new contributors. Each contributor gets a unique color and emoji combination based on their role and contribution order. ✨

### Contributors 🧑‍💻

<a href="https://github.com/iamawanishmaurya/NIET-Attendance-Tracker/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=iamawanishmaurya/NIET-Attendance-Tracker" />
</a>

![Alt](https://repobeats.axiom.co/api/embed/fa3995e7339da9586497c625c8613579549e4d78.svg "Repobeats analytics image")

## ⭐ Star History

<a href="https://www.star-history.com/#iamawanishmaurya/NIET-Attendance-Tracker&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=iamawanishmaurya/NIET-Attendance-Tracker&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=iamawanishmaurya/NIET-Attendance-Tracker&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=iamawanishmaurya/NIET-Attendance-Tracker&type=Date" />
 </picture>
</a>
