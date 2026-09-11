import os.path
import json
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_data_dir() -> str:
    """
    Returns the directory where application data is stored.
    Uses the same directory as the SQLite database by default.
    """
    # We avoid importing from app.config to prevent circular imports.
    # Instead, we use an environment variable or a default.
    data_dir = os.getenv("XO_OS_DATA_DIR")
    if data_dir:
        return data_dir
    # Default to ./data relative to the current working directory.
    return os.path.join(os.getcwd(), "data")


def get_credentials_path() -> str:
    """
    Returns the path to the Google OAuth2 client secrets file.
    """
    creds_path = os.getenv("XO_OS_GOOGLE_CREDENTIALS")
    if creds_path:
        return creds_path
    # Default to client_secret.json in the secrets directory.
    return os.path.join(os.getcwd(), "secrets", "client_secret.json")


def get_token_path() -> str:
    """
    Returns the path to the Google OAuth2 token file.
    """
    token_path = os.getenv("XO_OS_GOOGLE_TOKEN")
    if token_path:
        return token_path
    # Default to token.json in the secrets directory.
    return os.path.join(os.getcwd(), "secrets", "token.json")


def get_google_calendar_service():
    """
    Authenticates with Google Calendar API and returns a service object.
    Handles loading existing credentials, refreshing if necessary, or
    initiating the OAuth2 flow if no valid credentials are available.
    """
    creds = None
    token_file = get_token_path()
    # Check if token file exists and load credentials.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                get_credentials_path(), SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service