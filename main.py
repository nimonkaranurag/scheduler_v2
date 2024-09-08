from __future__ import print_function
import datetime
import os.path
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, Checkbutton, BooleanVar
from tkcalendar import DateEntry  # Import DateEntry for a date picker
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_api():
    """Authenticates and returns the credentials for Google Calendar API."""
    creds = None
    
    # Check if token.json exists and delete it to force re-authentication
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Authenticate and get credentials
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)

        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds


def add_event(service, summary, start_datetime, end_datetime, description='', repeating=False):
    """Adds an event to the user's Google Calendar."""
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Europe/Dublin',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Europe/Dublin',
        },
    }

    if repeating:
        # Add recurrence rule to repeat weekly
        event['recurrence'] = [
            'RRULE:FREQ=WEEKLY',
        ]

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

def create_event():
    """Handles the creation of a new event using the input from the GUI."""
    summary = summary_var.get()
    start_date = start_date_var.get()
    start_time = start_time_var.get()
    end_date = end_date_var.get()
    end_time = end_time_var.get()
    repeating = repeating_var.get()

    # Validating input
    if not summary or not start_date or not start_time or not end_date or not end_time:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        # Combine date and time into datetime strings
        start_datetime = f"{start_date}T{start_time}:00"
        end_datetime = f"{end_date}T{end_time}:00"

        creds = authenticate_google_api()
        service = build('calendar', 'v3', credentials=creds)
        add_event(service, summary, start_datetime, end_datetime, repeating=repeating)
        messagebox.showinfo("Success", "Event added to Google Calendar!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add event: {e}")

def setup_gui():
    """Sets up the GUI for inputting event details."""
    root = Tk()
    root.title("Google Calendar Event Creator")

    global summary_var, start_date_var, start_time_var, end_date_var, end_time_var, repeating_var
    summary_var = StringVar()
    start_date_var = StringVar()
    start_time_var = StringVar()
    end_date_var = StringVar()
    end_time_var = StringVar()
    repeating_var = BooleanVar()

    # Creating labels and entry widgets
    Label(root, text="Event Summary:").grid(row=0, column=0, padx=10, pady=5)
    Entry(root, textvariable=summary_var, width=30).grid(row=0, column=1, padx=10, pady=5)

    Label(root, text="Start Date:").grid(row=1, column=0, padx=10, pady=5)
    DateEntry(root, textvariable=start_date_var, date_pattern='yyyy-mm-dd').grid(row=1, column=1, padx=10, pady=5)

    Label(root, text="Start Time (HH:MM):").grid(row=2, column=0, padx=10, pady=5)
    Entry(root, textvariable=start_time_var, width=10).grid(row=2, column=1, padx=10, pady=5)

    Label(root, text="End Date:").grid(row=3, column=0, padx=10, pady=5)
    DateEntry(root, textvariable=end_date_var, date_pattern='yyyy-mm-dd').grid(row=3, column=1, padx=10, pady=5)

    Label(root, text="End Time (HH:MM):").grid(row=4, column=0, padx=10, pady=5)
    Entry(root, textvariable=end_time_var, width=10).grid(row=4, column=1, padx=10, pady=5)

    # Add repeating checkbox
    Checkbutton(root, text="Repeating (Weekly)", variable=repeating_var).grid(row=5, column=0, columnspan=2, pady=5)

    Button(root, text="Add Event", command=create_event).grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == '__main__':
    setup_gui()
