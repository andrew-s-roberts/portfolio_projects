# Import necessary libraries
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import calendar  # for calendar sidebar
from itertools import product  # for generating combinations

# Global Constants should be at top of file, below imports
# Default workday hours is included as a fallback in case no conditions are met.
# Also including the criteria and their states, defined by user input.
DEFAULT_WORKDAY_HOURS = 8
DEFAULT_WORKDAY_START = "09:00 AM"
CUSTOM_WORKDAY_START = "12:00 PM"
CRITERIA_STATES = {
    "Michelle": ["Off", "Sleeping/Working"],
    "AM Appointment": ["Yes Appointment", "No Appointment"],
    "Kids After School": ["Yes Tasks", "No Tasks"],
    "Cooking": ["Yes Cooking", "No Cooking"],
    "PM BJJ": ["Yes BJJ", "No BJJ"],
    "Weekend": ["Yes", "No"]
}

# Initialize session states to save input each time the user records information for a date
if 'daily_criteria_states' not in st.session_state:
    st.session_state.daily_criteria_states = []
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.today()

# Functions should all be defined together near the beginning of the program, not haphazardly throughout
# Function to return calendar information using calendar library
def display_calendar(year, month):
    cal = calendar.TextCalendar()
    return cal.formatmonth(year, month)


# Generate unique combinations of states
def generate_combinations(criteria_states):
    return list(product(*criteria_states.values()))


# Calculate end time and workday duration without using a default workday length
# In the following block, datetime.strptime() converts time strings to datetime objects compatible with timedelta
def calculate_time_and_duration(combination):
    michelle, am_appointment, kids_after_school, pm_bjj, cooking, weekend = combination
    workday_start = datetime.strptime(DEFAULT_WORKDAY_START, "%I:%M %p")
    end_time = None

    # Rules for calculating start time
    if am_appointment == "Yes Appointment":
        workday_start = datetime.strptime(CUSTOM_WORKDAY_START, "%I:%M %p")

    # Rules for calculating end time
    if pm_bjj == "Yes BJJ" and michelle == "Off" and cooking == "No Cooking":
        end_time = datetime.strptime("05:20 PM", "%I:%M %p")  # Set specific end time
    elif kids_after_school == "Yes Tasks":
        end_time = datetime.strptime("02:00 PM" if cooking == "Yes Cooking" else "03:00 PM", "%I:%M %p")
    elif pm_bjj == "Yes BJJ" and cooking == "Yes Cooking" and kids_after_school == "No Tasks":
        end_time = datetime.strptime("03:00 PM", "%I:%M %p")
    elif pm_bjj == "Yes BJJ" and cooking == "Yes Cooking" and kids_after_school == "Yes Tasks":
        end_time = datetime.strptime("02:00 PM", "%I:%M %p")
    elif weekend == "Yes" and cooking == "Yes Cooking":
        end_time = datetime.strptime("04:00 PM", "%I:%M %p")
    else:
        # Fallback to default workday length if none of the conditions are met
        end_time = datetime.strptime("05:00 PM", "%I:%M %p")

    # Calculate duration and return variables
    duration = end_time - workday_start
    return workday_start.strftime("%I:%M %p"), end_time.strftime("%I:%M %p"), str(duration)


# Determine "Best for BJJ" value
def determine_best_for_bjj(combination):
    michelle, am_appointment, kids_after_school, pm_bjj, cooking, weekend = combination
    if weekend == "Yes":
        return "Weekend"
    elif michelle == "Off" and cooking == "No Cooking" and kids_after_school == "No Tasks":
        return "Best"
    elif michelle != "Off" and cooking == "Yes Cooking" and kids_after_school == "Yes Tasks":
        return "Worst"
    elif michelle != "Off" and cooking == "Yes Cooking" and kids_after_school == "No Tasks":
        return "Possible"
    elif michelle != "Off" and cooking == "No Cooking" and kids_after_school == "Yes Tasks":
        return "Good"
    else:
        return "Possible"


# Function to recalculate the end time for a given row in DataFrame
def recalculate_end_time(row):
    combination = (row['Michelle'], row['AM Appointment'], row['Kids After School'], row['PM BJJ'], row['Cooking'], row['Weekend'])
    _, end_time, duration = calculate_time_and_duration(combination)
    row['Quittin Time'] = end_time
    row['Work Day Duration'] = duration
    return row


# Main Streamlit app
def main():
    st.title("Workday Scheduling Engine")
    # Input for the start date and the number of days to plan
    start_date = st.date_input("Start Date:", value=st.session_state.current_date)
    # Update session state current date based on user input
    st.session_state.current_date = start_date
    # Show the current date for which criteria are being entered
    st.write(f"Entering Criteria for Date: {st.session_state.current_date.strftime('%Y-%m-%d')}")
    # Headers for criteria section
    st.subheader("Scheduling Criteria")
    st.caption(
        "For each criterion, select the state which corresponds to that date. Then press the Record button to save those criteria, choose the next date and repeat. Once you have entered criteria for the whole planning period, press the calculate button. The app will return a matrix of dates with work day closing time and duration, as well as relative ease of planning evening jiujitsu classes"
    )

    # Inputs for the criteria states using radio buttons
    michelle_state = st.radio("Spouse status?", ["Off", "Sleeping/Working"])
    am_appointment = st.radio("AM Appointment?", ["Yes Appointment", "No Appointment"])
    kids_after_school_state = st.radio("Transporting Kids After School?", ["Yes Tasks", "No Tasks"])
    cooking_state = st.radio("Cooking supper?", ["Yes Cooking", "No Cooking"])
    pm_bjj_state = st.radio("PM BJJ Planned?", ["Yes BJJ", "No BJJ"])
    weekend_state = st.radio("Weekend?", ["Yes", "No"])

    # Button to record the criteria states for the current day
    if st.button("Record Data for This Day"):
        st.session_state.daily_criteria_states.append(
            (st.session_state.current_date, michelle_state, am_appointment, kids_after_school_state, pm_bjj_state, cooking_state, weekend_state))
        st.session_state.current_date += timedelta(days=1)

    # Button to start calculating the work schedule
    if st.button("Start Calculating"):
        with st.spinner():
            # Initialize an empty list to store the results
            results = []
            # Use st.session_state.daily_criteria_states here
            for day, michelle, am_appointment, kids_after_school, pm_bjj, cooking, weekend in st.session_state.daily_criteria_states:
                # Apply rules and calculate times and BJJ suitability 
                #rule_applied_combination = apply_rules((michelle, am_appointment, kids_after_school, pm_bjj, cooking, weekend))
				# apply_rules is not defined elsewhere in the code so I think this is a vertige of the earlier versions of the program and should be removed.
                workday_start, end_time, duration = calculate_time_and_duration(combination)
                best_for_bjj = determine_best_for_bjj(combination)

                # Append the results to the list, including workday_start
                results.append((day, workday_start, end_time, duration, michelle, am_appointment, kids_after_school, pm_bjj, cooking, weekend, best_for_bjj))

            # Create a DataFrame from the results
            columns = ["Date", "Punch In", "Quittin Time", "Work Day Duration", "Michelle", "AM Appointment", "Kids After School", "PM BJJ", "Cooking", "Weekend", "Best for BJJ"]
            df = pd.DataFrame(results, columns=columns)

            # Apply rules to the DataFrame to automatically change states after the fact based on criteria interactions
            df.loc[(df['Michelle'] == 'Sleeping/Working') | ((df['Michelle'] != 'Off') & (df['Weekend'] == 'Yes')), 'Cooking'] = 'Yes Cooking'
            df.loc[df['Weekend'] == 'Yes', ['PM BJJ', 'Kids After School']] = 'No BJJ', 'No Tasks'
            df.loc[df['Best for BJJ'].isin(['Best', 'Good']), 'PM BJJ'] = 'Yes BJJ'

            # Recalculate end time and workday duration based on changes stemming from rules above
            df = df.apply(lambda row: recalculate_end_time(row), axis=1)

            # Show the DataFrame in Streamlit
            st.write(df)

            # Exporting the DataFrame to a CSV file using Streamlit's built-in functionality
            csv = df.to_csv(index=False)
            st.download_button(
                "Download work schedule matrix as CSV",
                data=csv,
                file_name='work_schedule_matrix.csv',
                mime='text/csv'
            )
            st.success("Calculation Complete")

    # Reset Button to clear all recorded data and reset the date
    if st.button("Reset"):
        st.session_state.daily_criteria_states = []
        st.session_state.current_date = datetime.today()
        st.success("Data and date have been reset.")

    # Sidebar for Calendars
    st.sidebar.title("Three Month Overview")
    # Get current year and month
    current_year = datetime.today().year
    current_month = datetime.today().month
    # Calculate previous and next months
    prev_month, prev_year = (current_month - 1, current_year) if current_month > 1 else (12, current_year - 1)
    next_month, next_year = (current_month + 1, current_year) if current_month < 12 else (1, current_year + 1)
    # Display calendars
    st.sidebar.text(display_calendar(prev_year, prev_month))
    st.sidebar.text(display_calendar(current_year, current_month))
    st.sidebar.text(display_calendar(next_year, next_month))


# Run the app
if __name__ == "__main__":
    main()


# To run app on my machine, type: streamlit run C:\Users\user1\Desktop\JOB_HUNT\Scheduling\Scheduling_App_stream.py
