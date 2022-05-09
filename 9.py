import base64
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import mimetypes
import pickle
import os
from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import email


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']


def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    
    return service
  
def get_messages(service, user_id):
  try:
    result =  service.users().messages().list(userId=user_id).execute()
    print(result)
  except Exception as error:
    print('An error occurred: %s' % error)

def get_message(service, user_id, msg_id):
  try:
    result =  service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
    print(result)
  except Exception as error:
    print('An error occurred: %s' % error)
    
def get_mime_message(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()
    print('Message snippet: %s' % message['snippet'])
    msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
    mime_msg = email.message_from_string(msg_str)

    return mime_msg
  except Exception as error:
    print('An error occurred: %s' % error)
  
if __name__ == "__main__":
    service = get_service()
    user_id = 'me'
    # msg = create_message('hassan.jamal@mobylogix.com', 'hassankhan7571@gmail.com', 'Testing Gmail APi','This is the message body')
    # get_messages(service, user_id)
    ss = get_message(service, user_id,'1801de8c9e7a0ed0')
    print(ss)



