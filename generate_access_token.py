import requests

def generate_access_token():
    url = "https://www.arcgis.com/sharing/rest/oauth2/token"
    payload = 'client_id=######&client_secret=#####&grant_type=client_credentials&expiration=10'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.request("POST", url, headers=headers, data = payload)
    return response.json()['access_token']
