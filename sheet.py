from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

from flask import Flask, jsonify, request

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


def get_sheet(sheet_number,row):
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                majorDimension="ROWS",
                                range="Sheet"+str(sheet_number)+"!A1:E").execute()

        values = result.get('values', [])
        rowdata = values[row]
    except:
        rowdata  = {}

    header = values[0]
        
    data = dict(zip(header, rowdata))
    return data

def get_row_count(sheet_number):
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                majorDimension="ROWS",
                                range="Sheet"+str(sheet_number)+"!A1:E").execute()

        values = result.get('values', [])
        rowCount = len(values)
    except:
        rowCount = 0
    return rowCount

def write_sheet(sheet_number, rowdata):
    rowCount = get_row_count(sheet_number)

    try:
        result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                    range="Sheet"+str(sheet_number)+"!A"+str(rowCount+1),
                                    valueInputOption = "USER_ENTERED",
                                    body = rowdata 
                                    ).execute()
        data = result
    except:
        data = {}
    return data

app = Flask(__name__)

@app.route('/sheet/<int:sheet_number>/<int:row>', methods=['GET'])
def index(sheet_number,row):
    data = get_sheet(sheet_number,row)

    if data:
        message = "Data fetched successfully"
    else:
        message = "Data not found"

    res = {"message" : message, "data": data}
    
    return res

@app.route('/sheet/<int:sheet_number>',methods=['POST'])
def append_sheet(sheet_number):
    body = request.get_json()
    data = write_sheet(sheet_number,body)

    if data:
        message = "Data updated successfully"
    else:
        message = "Data not updated"

    res = {"message" : message, "data": data}
    
    return res
    

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)


    


