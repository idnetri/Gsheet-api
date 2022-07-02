from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

from flask import Flask, jsonify, request, make_response
from functools import wraps

import jwt
import datetime

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

app.config['SECRET_KEY'] = 'thisissecretkey'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        return  f(*args, **kwargs)
  
    return decorated

@app.route('/sheet/<int:sheet_number>/<int:row>', methods=['GET'])
@token_required
def index(sheet_number,row):
    data = get_sheet(sheet_number,row)

    print(type(data))

    if data:
        message = "Data fetched successfully"
    else:
        message = "Data not found"

    res = {"message" : message, "data": data}


    
    return jsonify(res),200

@app.route('/sheet/<int:sheet_number>',methods=['POST'])
@token_required
def append_sheet(sheet_number):
    body = request.get_json()
    data = write_sheet(sheet_number,body)

    if data:
        message = "Data updated successfully"
    else:
        message = "Data not updated"

    res = {"message" : message, "data": data}
    
    return jsonify(res),201

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message':'Can only accessed with valid token'})
    
@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'pass123':
        token = jwt.encode({'user':auth.username,'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify',401,{'WWW-Authenticate':'Basic realm="Login Required"'})

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)


    


