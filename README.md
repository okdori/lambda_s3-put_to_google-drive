# lambda_s3-put-to-google-drive

This project demonstrates how to upload files from AWS S3 to Google Drive using AWS Lambda. Before getting started, ensure that you have the credentials.json from Google Cloud Console and the necessary permissions set up for S3 and Lambda.



### Setup Instructions

#### 0. Code Download
Download the code as a ZIP file and unzip it.

#### 1. Configure Credentials
Open `first_pickle.py` and replace the value of `CREDENTIALS_FILE` with the path of your credentials.json file.
  
#### 2. Run first_pickle.py

```sh
cd lambda_s3-put_to_google-drive-master
pip install -r requirements.txt -t .
python3 first_pickle.py
```
This will open a Google Drive login popup.
Complete the login process.

#### 3. Generate token.pickle
After logging in, token.pickle will be generated in the same directory.

### 4. Update Google Drive Folder ID
Open `lambda_function.py` and replace the value of `SHARED_DRIVE_ID` with the folder ID of your Google Drive where you want to upload files.
  
-------

### Prepare Lambda Deployment

```sh
cd lambda_s3-put_to_google-drive-master
pip install -r requirements.txt -t .
zip -r ../my_lambda.zip .
```
