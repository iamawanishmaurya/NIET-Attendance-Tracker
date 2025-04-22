# NIET Attendance Tracker

## Description

This Python script helps students at NIET (Noida Institute of Engineering and Technology) track and analyze their attendance data fetched from the NIET Cloud portal. It provides features to view attendance summaries, detailed records, calculate requirements to meet attendance goals, estimate leave allowances, and project future attendance.

## Features

* **Fetch or Load Data**: Retrieve attendance data directly from NIET Cloud using your session's `JSESSIONID` or load previously saved data from a local `attendence.json` file.
* **Attendance Summary**: View a summary table showing attendance counts (present/total) and percentages for each subject, along with an overall total.
* **Detailed Subject Attendance**: See a detailed log of attendance for any specific subject, including date, lecture time, session, and status (Present/Absent).
* **Target Percentage Calculation**: Calculate the exact number of consecutive classes you need to attend to reach a specific target attendance percentage (e.g., 85%) and estimates the number of days this will take based on a typical class schedule.
* **Leave Allowance**: Estimate how many classes you can miss while maintaining a target attendance percentage (e.g., 85%) and approximates the corresponding number of leave days.
* **Future Projection**: Project your attendance percentage by a future date, considering the typical weekly class schedule (7 classes Mon-Fri, 6 classes Sat) and allowing for custom holidays. See projections based on different future attendance rates (e.g., if you attend 100% of future classes, 90%, etc.).
* **Attendance Alerts**: Get immediate alerts if your current overall attendance is below 85%, along with the number of classes needed to reach the target.
* **Interactive CLI**: Easy-to-use command-line interface with menu options to access different features.

## Requirements

* Python 3.x
* Required Python libraries:
    * `requests`
    * `pandas`
    * `tabulate`

## Installation

1.  **Clone the repository (or download the script):**
    ```bash
    git clone https://github.com/iamawanishmaurya/NIET-Attendance-Tracker.git
    cd NIET-Attendance-Tracker
    ```
    (Replace `<your-repository-url>` and `<your-repository-directory>` accordingly)

2.  **Install the required libraries:**
    ```bash
    pip install requests pandas tabulate
    ```

## Usage

1.  **Run the script:**
    ```bash
    python niet_attendance_tracker.py
    ```

2.  **Choose Data Source:**
    * **Option 1: Fetch from NIET Cloud:**
        * You will be prompted to enter your `JSESSIONID`.
        * **How to get JSESSIONID:**
            1.  Log in to the NIET Cloud portal (https://nietcloud.niet.co.in/) in your web browser.
            2.  Open your browser's Developer Tools (usually by pressing F12).
            3.  Go to the "Application" (in Chrome) or "Storage" (in Firefox) tab.
            4.  Find the "Cookies" section and select the `nietcloud.niet.co.in` domain.
            5.  Locate the cookie named `JSESSIONID` and copy its value.
            6.  Paste this value into the script when prompted.
        * The script will attempt to fetch the data and save it as `attendence.json` in the same directory.
    * **Option 2: Load from local JSON file:**
        * Enter the path to your JSON file (e.g., `attendence.json`). Press Enter to use the default `attendence.json`.

3.  **View Summary:** The script will display the overall attendance summary. If your attendance is below 85%, an alert will be shown.

4.  **Use Additional Features:**
    * Follow the menu prompts to:
        * View detailed attendance for a specific subject.
        * Calculate leave allowance.
        * Project future attendance (you'll need to provide an end date and optionally list holidays).
        * Calculate classes needed to reach a custom target percentage.
        * Exit the program.

## Disclaimer

This script interacts with the NIET Cloud website. Use it responsibly. The accuracy of the fetched data depends on the NIET Cloud portal. Ensure your `JSESSIONID` is kept private. The developers of this script are not responsible for any issues arising from its use.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the script.
