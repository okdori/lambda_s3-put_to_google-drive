import os
import pickle
import json
import boto3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from urllib.parse import unquote


CREDENTIALS_FILE = '/var/task/credentials.json'
FIRST_TOKEN_PICKLE_FILE = '/var/task/token.pickle'
TOKEN_PICKLE_FILE = '/tmp/token.pickle'
SHARED_DRIVE_ID = 'your-google-drive-folder-id'
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def download_from_s3(bucket_name, s3_key, download_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, download_path)
    
def authenticate_gdrive():
    creds = None
    # Load credentials from the token file stored in Lambda's /tmp/ directory
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Perform authentication if no valid credentials exist or they are expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_PICKLE_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Error occurred while refreshing token: {e}")
                creds = None
        if not creds:
            raise Exception('No valid Google Drive credentials found. Authentication is required.')

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(s3_key, file_path):
    drive_service = authenticate_gdrive()
    
    file_metadata = {
        'name': s3_key,
        'parents': [SHARED_DRIVE_ID]
    }
    media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)

    request = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    )

    # Execute the upload request
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    
    print(f'File ID: {response.get("id")}')
    return response.get('id')


def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']
        s3_key = unquote(s3_key) # Decode file name from URL encoding
        download_path = f'/tmp/{s3_key}'

        # Refresh token initially
        with open(FIRST_TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_PICKLE_FILE, 'wb') as token:
                    pickle.dump(creds, token)

        # Download file from S3
        download_from_s3(bucket_name, s3_key, download_path)
        print('Temporary file download complete')
        
        # Upload file to Google Drive
        drive_file_id = upload_to_drive(s3_key, download_path)
        print('Google Drive upload complete')

        return {
            'statusCode': 200,
            'body': json.dumps(f'File has been uploaded to Google Drive. File ID: {drive_file_id}')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error occurred: {e}')
        }