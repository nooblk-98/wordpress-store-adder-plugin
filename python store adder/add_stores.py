import requests
import time

# Define the list of store locations
locations = [
    {
        "name": "Crown Stores",
        "address": "No.71,Periyakade,Mannar.",
        "city": "Mannar",
        "state": "Mannar",
        "country": "SRILANKA"
    },
    {
        "name": "Colombo Essence House",
        "address": "No.109,K K S Road,Jaffna.",
        "city": "Jaffna",
        "state": "Jaffna",
        "country": "SRILANKA"
    },
    {
        "name": "Chithaara (Beauty Parlour And Fitness Centre)",
        "address": "No 18,2nd Bazzar Street,Grand Bazzar,Mannara.",
        "city": "Mannar",
        "state": "Mannar",
        "country": "SRILANKA"
    }
]

# Specify the API endpoint
api_endpoint = 'https://demo-store.itsnooblk.xyz/wp-json/store-locator/v1/add-store'

# Set the Basic Authentication credentials
auth_credentials = ('admin', 'admin')

# Loop through the locations and send a POST request for each one
for location in locations:
    response = requests.post(api_endpoint, json=location, auth=auth_credentials)
    if response.status_code == 200:
        print(f"Store added successfully: {location['name']}")
    else:
        print(f"Failed to add store: {location['name']} - {response.text}")
    time.sleep(1)  # Add a delay between requests for stability
