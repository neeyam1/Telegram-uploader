import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def get_credentials(credentials_file, token_file):
    """Gets valid user credentials from storage or initiates OAuth flow."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None

        if not creds:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Credentials file '{credentials_file}' not found. Please download it from Google Cloud Console.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            # Force consent prompt to ensure user sees the checkboxes
            creds = flow.run_local_server(port=0, prompt='consent')
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
    # Debug: Print granted scopes
    if creds:
        print(f"Granted scopes: {creds.scopes}")
            
    return creds

def get_photos_service(credentials_file, token_file):
    """Builds and returns the Google Photos API service."""
    creds = get_credentials(credentials_file, token_file)
    service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    return service
