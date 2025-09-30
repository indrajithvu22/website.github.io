import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Google Sheets API Connection ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

try:
    # IMPORTANT: Ensure your sheet has columns named 'Name' and 'RegisterNumber'
    sheet = client.open("Registrations").sheet1
except gspread.exceptions.SpreadsheetNotFound:
    print("Error: Spreadsheet 'Registrations' not found.")
    exit()

# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Handles the registration request."""
    data = request.get_json()
    name = data.get('name')
    reg_num = data.get('register_number')

    if not name or not reg_num:
        return jsonify({'status': 'error', 'message': 'Name and Register Number are required.'}), 400

    records = sheet.get_all_records()
    
    # --- THIS IS THE DUPLICATE CHECK ---
    # It iterates through each row to find a match for both Name and Register Number.
    for record in records:
        # .strip() removes accidental spaces from user input for a reliable check.
        if str(record.get('Name')).strip() == name.strip() and str(record.get('RegisterNumber')).strip() == reg_num.strip():
            # If a match is found, it returns the "Already registered" message.
            return jsonify({'status': 'exists', 'message': 'Already registered'}), 409 # 409 Conflict

    # If the loop finishes without finding a duplicate, add the new entry.
    try:
        sheet.append_row([name, reg_num])
        return jsonify({'status': 'success', 'message': 'Successfully registered'}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True)