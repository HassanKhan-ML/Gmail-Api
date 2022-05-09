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
    
    # results = service.users().messages().list(userId='me',labelIds = ['INBOX']).execute()
    # messages = results.get('messages', [])
    
    # if not messages:
    #     print ("No messages found.")
    # else:
    #     print ("Message snippets:")
    #     for message in messages:
    #         msg = service.users().messages().get(userId='me', id=message['id']).execute()
    #         print(msg['snippet'])

    return service

def search_message(service, user_id, search_string):
    """
    Search the inbox for emails using standard gmail search parameters
    and return a list of email IDs for each result
    PARAMS:
        service: the google api service object already instantiated
        user_id: user id for google api service ('me' works here if
        already authenticated)
        search_string: search operators you can use with Gmail
        (see https://support.google.com/mail/answer/7190?hl=en for a list)
    RETURNS:
        List containing email IDs of search query
    """
    try:
        # initiate the list for returning
        list_ids = []

        # get the id of all messages that are in the search string
        search_ids = service.users().messages().list(userId=user_id, q=search_string).execute()
        # if there were no results, print warning and return empty string
        print(search_ids)
        messages = search_ids.get('messages')
        
        for msg in messages:
            # txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            msg = get_mime_message(service, user_id, msg['id'])
            
            print(msg)


        # try:
        #     ids = search_ids['messages']
        # except KeyError:
        #     print("WARNING: the search queried returned 0 results")
        #     print("returning an empty string")
        #     return ""
        # if len(ids)>1:
        #     for msg_id in ids:
        #         list_ids.append(msg_id['id'])
        #     return(list_ids)
        # else:
        #     list_ids.append(ids['id'])
        #     return list_ids
        
    except Exception as e:
        print('An error occurred: {}'.format(e))

  
def get_message(service, user_id, msg_id):
    """
    Search the inbox for specific message by ID and return it back as a 
    clean string. String may contain Python escape characters for newline
    and return line. 
    
    PARAMS
        service: the google api service object already instantiated
        user_id: user id for google api service ('me' works here if
        already authenticated)
        msg_id: the unique id of the email you need
    RETURNS
        A string of encoded text containing the message body
    """
    try:
        # grab the message instance
        message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()

        # decode the raw string, ASCII works pretty well here
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        # grab the string from the byte object
        mime_msg = email.message_from_bytes(msg_str)

        # check if the content is multipart (it usually is)
        content_type = mime_msg.get_content_maintype()
        if content_type == 'multipart':
            # there will usually be 2 parts the first will be the body in text
            # the second will be the text in html
            parts = mime_msg.get_payload()

            # return the encoded text
            final_content = parts[0].get_payload()
            return final_content

        elif content_type == 'text':
            return mime_msg.get_payload()
        else:
            return ""
            # print("\nMessage is not text or multipart, returned an empty string")
    # unsure why the usual exception doesn't work in this case, but 
    # having a standard Exception seems to do the trick
    except Exception as e:
        print('An error occurred: {}'.format(e))

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
    
    # ss = search_message(service,user_id,'subject:Login failed ')
    ss = search_message(service,user_id,'from:hassankhan7571@gmail.com')
    # ss = get_message(service, user_id, '1804b3ff2a848444')
    # ss = get_message(service, user_id, '18017362cdd75371')
  
    print(ss)


