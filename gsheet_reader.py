import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


RANGE_NAME = 'Weekly Attendance (2020)!A1:AV20'

SPREADSHEET_ID = {
    'SA A': '1jublOuZOpkQwfdgXLNmh1VCA_ha4JeLJfby_eOHpw4Y',
    'SA B': '1coHukM-iEoVxlsOV7JgLLusRkWYh8V9HIrK5RAT5H_E',
    'SA C': '11cg7jNzH5rczIYpbUl7g4_2HZKcJzqlw-dN6cDoqEMo',
    'CJ A': '1oqfbYg7nTktcgPA8QQjULfo4Jsn42oDtjG4jLvZEyho',
    'CJ B': '1OxDDWTMyxJK5OQJoBLhVZ3b-GgBI4kYfBlNVyE-sKfw',
    'CJ C': '1FOhZMv_uEyOhDUF_wRunweRDPmjNLygMfFvBsqSShDA',
}


def get_cg_data(CG) -> str:
    """Returns the value of CG data"""
    assert(CG in SPREADSHEET_ID.keys())
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID[CG],
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    # print(values)
    df_temp = pd.DataFrame(values)
    df = df_temp[1:]
    df.columns = df_temp.iloc[0]
    df.reset_index(inplace=True, drop=True)
    return df




if __name__ == '__main__':
    print(get_cg_data('CJ A'))