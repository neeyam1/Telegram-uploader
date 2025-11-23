import json
import requests

def debug_google_photos():
    print("Reading token_new.json...")
    try:
        with open('token_new.json', 'r') as f:
            token_data = json.load(f)
            access_token = token_data.get('token')
            
        if not access_token:
            print("Error: No access token found in token_new.json")
            return

        print(f"Access Token found (starts with): {access_token[:10]}...")
        
        url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        
        print(f"Checking token info at: {url}")
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)
        
    except FileNotFoundError:
        print("Error: token_new.json not found. Please run main.py first to generate it.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    debug_google_photos()
