import json
import pandas as pd
import os
import requests
from datetime import datetime, timedelta, date
from tabulate import tabulate
import calendar
import math

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_attendance_data(jsessionid):
    """
    Fetch attendance data from nietcloud using the provided JSESSIONID.
    """
    cookies = {
        '_ga_70Q2G5SZRG': 'GS1.1.1745255234.3.1.1745255594.0.0.0',
        '_ga': 'GA1.1.203454139.1745078541',
        '__utma': '225447301.203454139.1745078541.1745082354.1745255233.3',
        '__utmz': '225447301.1745078542.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        'JSESSIONID': jsessionid,
        '__utmc': '225447301',
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://nietcloud.niet.co.in/studentCourseFileNew.htm?shwA=%2700A%27',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    params = {
        'termId': '2',
        'refreshData': '0',
    }
    
    try:
        response = requests.get(
            'https://nietcloud.niet.co.in/getSubjectOnChangeWithSemId1.json',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        
        if response.status_code == 200:
            # Save the fetched data to a JSON file
            with open('attendence.json', 'w') as f:
                json.dump(response.json(), f, indent=4)
            print("Successfully fetched and saved attendance data to 'attendence.json'")
            return response.json()
        else:
            print(f"Error: Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: Failed to fetch data. {str(e)}")
        return None

def load_attendance_data(json_file):
    """
    Load attendance data from a JSON file.
    """
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{json_file}' is not a valid JSON file.")
        return None

def extract_summary_data(data):
    """
    Extract summary data for all subjects.
    """
    summary = []
    total_present = 0
    total_classes = 0
    
    for subject in data:
        present_count = int(subject.get('presentCount', 0))
        absent_count = int(subject.get('absentCount', 0))
        total_count = present_count + absent_count
        
        # Calculate percentage
        percentage = (present_count / total_count * 100) if total_count > 0 else 0
        
        summary.append({
            'Code': subject.get('subjectCode', ''),
            'Course Name': subject.get('subject', ''),
            'Attendance Count': f"{present_count}/{total_count}",
            'Percentage': round(percentage, 2)
        })
        
        total_present += present_count
        total_classes += total_count
    
    # Calculate overall percentage
    overall_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
    
    # Add total row
    summary.append({
        'Code': '',
        'Course Name': 'TOTAL',
        'Attendance Count': f"{total_present}/{total_classes}",
        'Percentage': round(overall_percentage, 2)
    })
    
    return summary, total_present, total_classes

def extract_detailed_attendance(subject_data):
    """
    Extract detailed attendance for a specific subject.
    """
    details = []
    
    # Parse attendance data string
    attendance_str = subject_data.get('studentAttendanceData', '')
    attendance_entries = attendance_str.split(';')
    
    sr_no = 1
    for entry in attendance_entries:
        if not entry:
            continue
        
        parts = entry.split('^^^')
        if len(parts) >= 6:
            date_str, start_time, end_time, status, session, _ = parts[:6]
            
            try:
                # Parse the date string
                date_obj = datetime.strptime(date_str, '%b %d, %Y')
                formatted_date = date_obj.strftime('%b %d, %Y')
                
                details.append({
                    'Sr. No': sr_no,
                    'Date': formatted_date,
                    'Lecture Time': f"{start_time} - {end_time}",
                    'Session': session,
                    'Status': status
                })
                sr_no += 1
            except ValueError:
                # Skip entries with invalid date format
                continue
    
    return details

def display_summary(summary_data):
    """
    Display summary data in a tabular format.
    """
    df = pd.DataFrame(summary_data)
    print("\n=== Attendance Summary ===\n")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def display_subject_details(subject, details_data):
    """
    Display detailed attendance for a specific subject.
    """
    df = pd.DataFrame(details_data)
    print(f"\n=== Attendance Details of {subject} ===\n")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def calculate_classes_needed_for_target(total_present, total_classes, target_percentage=85):
    """
    Calculate how many consecutive classes need to be attended to reach the target percentage.
    """
    current_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
    
    if current_percentage >= target_percentage:
        return 0, 0, current_percentage
    
    # Formula to find how many consecutive classes need to be attended to reach target:
    # (total_present + x) / (total_classes + x) ≥ target_percentage/100
    # Solving for x:
    # x ≥ (target_percentage*total_classes - 100*total_present) / (100 - target_percentage)
    
    # Calculate the minimum number of consecutive classes needed
    numerator = (target_percentage * total_classes - 100 * total_present)
    denominator = (100 - target_percentage)
    classes_needed = math.ceil(numerator / denominator)
    
    # Calculate approximate days needed
    # Assuming: 7 classes per day Mon-Fri, 6 on Saturday, 0 on Sunday
    classes_per_week = 7 * 5 + 6  # 41 classes per week
    
    # Approximate days calculation (slightly conservative)
    week_days = int(classes_needed / 7) + (1 if classes_needed % 7 > 0 else 0)
    saturdays = int(classes_needed / 6) + (1 if classes_needed % 6 > 0 else 0)
    
    # Rough estimation of days, accounting for weekends
    approx_days = math.ceil(classes_needed / 7)  # Very rough estimate
    
    # More accurate calculation: simulate the daily schedule
    days_needed = 0
    classes_remaining = classes_needed
    current_day = date.today()
    
    while classes_remaining > 0:
        days_needed += 1
        current_day += timedelta(days=1)
        day_of_week = current_day.weekday()  # 0=Monday, 6=Sunday
        
        if day_of_week < 5:  # Monday to Friday
            classes_remaining -= min(7, classes_remaining)
        elif day_of_week == 5:  # Saturday
            classes_remaining -= min(6, classes_remaining)
        # Sunday has no classes, but we still count it as a day
    
    # Calculate new percentage after attending these classes
    new_percentage = ((total_present + classes_needed) / (total_classes + classes_needed)) * 100
    
    return classes_needed, days_needed, new_percentage

def calculate_leave_allowance(total_present, total_classes, target_percentage=85):
    """
    Calculate how many classes can be missed while maintaining the target attendance percentage.
    Also calculate days of leave possible.
    """
    # Current percentage
    current_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
    
    # Calculate maximum absences allowed to maintain target percentage
    max_future_absences = int((total_present * 100 / target_percentage) - total_classes)
    
    # Convert to approximate days
    # For a conservative estimate, use the minimum classes per day (6)
    min_days_leave = max_future_absences // 6
    
    # For a more optimistic estimate, use average classes per day ((7*5 + 6)/6 ≈ 6.5)
    avg_classes_per_day = (7 * 5 + 6) / 6  # Average across a week
    avg_days_leave = max_future_absences / avg_classes_per_day
    
    # More accurate calculation considering weekly schedule
    days_leave = 0
    absences_remaining = max_future_absences
    
    if absences_remaining > 0:
        # Calculate how many full weeks of leave are possible
        full_weeks = absences_remaining // 41  # 41 classes per week
        days_leave += full_weeks * 7
        absences_remaining -= full_weeks * 41
        
        # Calculate remaining days
        current_day = 0  # 0=Monday
        while absences_remaining > 0:
            if current_day < 5:  # Monday to Friday
                absences_to_use = min(7, absences_remaining)
            elif current_day == 5:  # Saturday
                absences_to_use = min(6, absences_remaining)
            else:  # Sunday
                absences_to_use = 0
            
            absences_remaining -= absences_to_use
            if absences_to_use > 0:
                days_leave += 1
            
            current_day = (current_day + 1) % 7
    
    return {
        'current_percentage': current_percentage,
        'target_percentage': target_percentage,
        'max_absences': max_future_absences if max_future_absences >= 0 else 0,
        'approx_days_leave': round(min_days_leave, 1),
        'detailed_days_leave': days_leave
    }

def calculate_future_attendance(total_present, total_classes, end_date_str, holidays=None):
    """
    Calculate projected attendance by the specified end date with the weekly schedule:
    - 7 classes each day Monday to Friday (35 per week)
    - 6 classes on Saturday
    - No classes on Sunday
    - Accounts for specified holidays
    """
    try:
        # Parse end date
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        # Current date
        current_date = date.today()
        
        if current_date >= end_date:
            return {
                'error': 'End date must be in the future.'
            }
        
        # Initialize counters
        future_classes = 0
        future_days = []
        
        # Process each day
        while current_date < end_date:
            current_date += timedelta(days=1)
            
            # Skip holidays
            if holidays and current_date.strftime("%Y-%m-%d") in holidays:
                continue
                
            # Calculate classes based on the day of the week
            day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
            
            if day_of_week < 5:  # Monday to Friday
                future_classes += 7
                future_days.append((current_date, 7))
            elif day_of_week == 5:  # Saturday
                future_classes += 6
                future_days.append((current_date, 6))
            # Sunday has no classes
        
        # Calculate projected attendance
        future_total_classes = total_classes + future_classes
        
        # Calculate scenarios for different attendance levels
        scenarios = []
        
        # Classes needed to reach 85%
        classes_needed_85 = 0
        if (total_present / future_total_classes) * 100 < 85:
            # Need to find x where (total_present + x) / future_total_classes >= 0.85
            classes_needed_85 = math.ceil(0.85 * future_total_classes - total_present)
        
        for future_attendance_percentage in [100, 95, 90, 85, 75, 50, 0]:
            future_present = int(future_classes * (future_attendance_percentage / 100))
            projected_total_present = total_present + future_present
            projected_percentage = (projected_total_present / future_total_classes) * 100
            
            # Calculate days needed for this attendance level
            days_needed = 0
            classes_to_attend = int(future_classes * (future_attendance_percentage / 100))
            classes_remaining = classes_to_attend
            
            # Calculate days required for this many classes
            days_for_classes = 0
            remaining_classes = classes_to_attend
            
            for day_date, day_classes in future_days:
                if remaining_classes <= 0:
                    break
                
                classes_today = min(day_classes, remaining_classes)
                remaining_classes -= classes_today
                
                if classes_today > 0:
                    days_for_classes += 1
            
            scenarios.append({
                'future_attendance': future_attendance_percentage,
                'classes_to_attend': classes_to_attend,
                'days_to_attend': days_for_classes,
                'projected_total': f"{projected_total_present}/{future_total_classes}",
                'projected_percentage': round(projected_percentage, 2)
            })
        
        return {
            'current_total': f"{total_present}/{total_classes}",
            'current_percentage': round((total_present / total_classes) * 100, 2),
            'future_classes': future_classes,
            'future_total_classes': future_total_classes,
            'classes_needed_85': classes_needed_85,
            'scenarios': scenarios
        }
        
    except ValueError:
        return {
            'error': 'Invalid date format. Please use YYYY-MM-DD.'
        }

def display_leave_allowance_results(result):
    """
    Display leave allowance calculation results.
    """
    print("\n=== Leave Allowance Calculator ===\n")
    print(f"Current attendance: {result['current_percentage']:.2f}%")
    print(f"Target attendance: {result['target_percentage']:.2f}%")
    
    if result['current_percentage'] >= result['target_percentage']:
        print(f"\nYou can miss up to {result['max_absences']} more classes while maintaining {result['target_percentage']}% attendance.")
        print(f"This is approximately {result['detailed_days_leave']} days of leave (considering your class schedule).")
    else:
        print(f"\nYour current attendance is below the target of {result['target_percentage']}%.")
        
        # Calculate how many classes needed to reach target
        classes_needed, days_needed, new_percentage = calculate_classes_needed_for_target(
            total_present, total_classes, result['target_percentage'])
            
        print(f"You need to attend at least {classes_needed} consecutive classes to reach {result['target_percentage']}% attendance.")
        print(f"This will take approximately {days_needed} days of full attendance.")
        print(f"After attending these classes, your attendance will be approximately {new_percentage:.2f}%.")

def display_future_attendance_results(result):
    """
    Display future attendance calculation results.
    """
    if 'error' in result:
        print(f"\nError: {result['error']}")
        return
    
    print("\n=== Future Attendance Projection ===\n")
    print(f"Current attendance: {result['current_total']} ({result['current_percentage']}%)")
    print(f"Future classes till end date: {result['future_classes']}")
    print(f"Total classes by end date: {result['future_total_classes']}")
    
    if result['current_percentage'] < 85:
        print(f"\nTo reach 85% attendance by the end date, you need to attend at least {result['classes_needed_85']} classes.")
    
    print("\nProjected attendance based on future attendance rate:")
    scenarios_data = []
    for s in result['scenarios']:
        scenarios_data.append({
            'Future Attendance Rate': f"{s['future_attendance']}%",
            'Classes to Attend': s['classes_to_attend'],
            'Days to Attend': s['days_to_attend'],
            'Projected Total': s['projected_total'],
            'Projected Percentage': f"{s['projected_percentage']}%"
        })
    
    print(tabulate(scenarios_data, headers='keys', tablefmt='grid', showindex=False))

def main():
    """
    Main function to run the attendance data extraction.
    """
    print("=== NIET Attendance Tracker ===\n")
    
    # Ask user to choose data source
    print("How would you like to get attendance data?")
    print("1. Fetch from NIET Cloud (requires JSESSIONID)")
    print("2. Load from local JSON file")
    
    try:
        choice = int(input("\nEnter your choice (1 or 2): "))
        
        if choice == 1:
            # Get JSESSIONID from user
            jsessionid = input("\nEnter your JSESSIONID from NIET Cloud: ")
            data = fetch_attendance_data(jsessionid)
            if not data:
                return
        
        elif choice == 2:
            # File path
            json_file = input("\nEnter the path to your attendance JSON file (or press Enter for default 'attendence.json'): ")
            if not json_file:
                json_file = 'attendence.json'
            
            # Load data
            data = load_attendance_data(json_file)
            if not data:
                return
        
        else:
            print("Invalid choice. Exiting program.")
            return
    
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Extract and display summary
    summary, total_present, total_classes = extract_summary_data(data)
    display_summary(summary)
    
    # Immediately show key information if attendance is below 85%
    current_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
    if current_percentage < 85:
        classes_needed, days_needed, new_percentage = calculate_classes_needed_for_target(
            total_present, total_classes, 85)
        
        print("\n⚠️ ATTENDANCE ALERT ⚠️")
        print(f"Your current attendance ({current_percentage:.2f}%) is below the 85% requirement.")
        print(f"You need to attend at least {classes_needed} consecutive classes to reach 85%.")
        print(f"This will take approximately {days_needed} days of full attendance.")
    
    # Menu for additional features
    while True:
        print("\n=== Additional Features ===")
        print("1. View detailed attendance for a subject")
        print("2. Calculate leave allowance (85% target)")
        print("3. Project future attendance")
        print("4. Calculate classes needed to reach target percentage")
        print("0. Exit")
        
        try:
            choice = int(input("\nEnter your choice: "))
            
            if choice == 0:
                print("Exiting program.")
                break
                
            elif choice == 1:
                # Create subject list for selection
                subject_list = []
                for i, subject in enumerate(data, 1):
                    subject_name = subject.get('subject', '')
                    subject_code = subject.get('subjectCode', '')
                    subject_list.append((i, subject_name, subject_code))
                
                # User selection
                print("\nAvailable subjects:")
                for i, name, code in subject_list:
                    print(f"{i}. {name} [{code}]")
                
                try:
                    subject_choice = int(input("\nEnter the number of the subject to view detailed attendance: "))
                    
                    if 1 <= subject_choice <= len(subject_list):
                        selected_index = subject_choice - 1
                        selected_subject = data[selected_index]
                        subject_name = selected_subject.get('subject', '')
                        
                        # Extract and display detailed attendance
                        details = extract_detailed_attendance(selected_subject)
                        display_subject_details(subject_name, details)
                    else:
                        print("Invalid choice. Please try again.")
                
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    
            elif choice == 2:
                # Calculate leave allowance
                result = calculate_leave_allowance(total_present, total_classes, 85)
                display_leave_allowance_results(result)
                
            elif choice == 3:
                # Project future attendance
                end_date_str = input("\nEnter the end date (YYYY-MM-DD): ")
                
                # Ask for holidays
                holidays = []
                add_holidays = input("Do you want to add holidays? (y/n): ").lower()
                if add_holidays == 'y':
                    print("Enter holiday dates (YYYY-MM-DD), one per line. Enter a blank line when done.")
                    while True:
                        holiday = input("Holiday date (or blank to finish): ")
                        if not holiday:
                            break
                        holidays.append(holiday)
                
                result = calculate_future_attendance(total_present, total_classes, end_date_str, holidays)
                display_future_attendance_results(result)
                
            elif choice == 4:
                # Calculate classes needed to reach target percentage
                target = float(input("\nEnter target attendance percentage: "))
                classes_needed, days_needed, new_percentage = calculate_classes_needed_for_target(
                    total_present, total_classes, target)
                
                print(f"\nTo reach {target}% attendance:")
                print(f"- You need to attend {classes_needed} consecutive classes")
                print(f"- This will take approximately {days_needed} days of full attendance")
                print(f"- After attending these classes, your attendance will be {new_percentage:.2f}%")
                
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
