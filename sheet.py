from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

from flask import Flask

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of spreadsheet.
SPREADSHEET_ID = '133xPY8o2-1-tPNbkNolVVhFXoifXYlrQcU-5EPahThc'

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()


def get_sheet(sheet_id,row):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            majorDimension="ROWS",
                            range="Sheet"+str(sheet_id)+"!A1:E").execute()
    values = result.get('values', [])

    if row > 0:
        index = row-1
    jsonStr = json.dumps(values[index])
    
    return jsonStr

app = Flask(__name__)

@app.route('/sheet/<int:sheet_id>/<int:row>', methods=['GET'])
def index(sheet_id,row):
    data = get_sheet(sheet_id,row)

    return { "row" : data }

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)


    


