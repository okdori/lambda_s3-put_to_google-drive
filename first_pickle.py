import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_FILE = 'your-credentials.json-path'
TOKEN_PICKLE_FILE = 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)

if __name__ == '__main__':
    main()