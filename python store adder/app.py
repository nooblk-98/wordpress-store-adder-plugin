from flask import Flask, request, render_template, jsonify, send_file
import pandas as pd
import json
import tempfile
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_excel_to_json():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    sheet_name = request.form.get('sheet_name')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and sheet_name:
        df = pd.read_excel(file, sheet_name=sheet_name)
        selected_columns = df[['NAMECUST', 'ADDRESS', 'CITY', 'DISTRICT']]
        renamed_columns = selected_columns.rename(columns={
            'NAMECUST': 'name',
            'ADDRESS': 'address',
            'CITY': 'city',
            'DISTRICT': 'state'
        })
        renamed_columns['country'] = 'SRILANKA'
        json_data = renamed_columns.to_json(orient='records', indent=4)

        # Create a temporary file to store the JSON data
        temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        with open(temp_file.name, 'w') as file:
            json.dump(json.loads(json_data), file, indent=4)

        # Send the file as a downloadable response
        return send_file(temp_file.name, as_attachment=True, download_name='converted_data.json')

    return jsonify({'error': 'Missing sheet name'}), 400

@app.route('/import-stores', methods=['POST'])
def import_stores():
    if 'json_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    json_file = request.files['json_file']

    if json_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if json_file:
        # Load the JSON data from the uploaded file
        stores = json.load(json_file)

        # Specify the API endpoint and Basic Authentication credentials
        api_endpoint = 'https://demo-store.itsnooblk.xyz/wp-json/store-locator/v1/add-store'
        auth_credentials = ('admin', 'admin')

        # Loop through the stores and send a POST request for each one
        for store in stores:
            response = requests.post(api_endpoint, json=store, auth=auth_credentials)
            if response.status_code != 200:
                return jsonify({'error': f"Failed to add store: {store['name']} - {response.text}"}), 500

        return jsonify({'message': 'Stores imported successfully'})

    return jsonify({'error': 'Invalid file'}), 400

if __name__ == '__main__':
    app.run(debug=True)
