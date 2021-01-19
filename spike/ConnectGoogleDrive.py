# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 22:03:11 2021

@author: Jian Cao

Download and upload files from/to Google Drive
"""

## Set environment ------------------------------------------------------------
import io
import os
import pickle
import os.path
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import shutil
import subprocess

## Define class ---------------------------------------------------------------
class ConnectGoogleDrive:
    """Object that connects Google Drive
    Functions:
        .SeachItem()
    """

    def __init__(self, token_path):
        # Define the scopes 
        SCOPES = ['https://www.googleapis.com/auth/drive']
        # read token
        creds = None
        token_path = self._check_path(token_path)
        if os.path.exists(token_path + 'token.pickle'):
            with open(token_path + 'token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path + 'token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)
        print("Connected to Google Drive")


    def _check_path(self, path):
        if path[-1] != '/':
            path = path + '/'
        return(path)


    def ListItems(self, item_name, parents):
        """List items (file/folder) by name or parents 
        Parameters:     
           item_name (str): name of file/folder
           parents (str): target folder ID 
        Returns:     
           list(dict): list of {id, name, parents}
        """ 
        if not item_name and not parents:
            print('No rules specified, exiting...')
            return None
        page_token = None
        item_list = []
        if item_name and parents:
            print('Please specify either ITEM_NAME or PARENTS, not both...')
            return None
        elif item_name:
            query = "name='{}'".format(item_name)
        else:
            query = "'{}' in parents".format(parents)
        while True:     
            response = self.service.files().list(
                        q = query,
                        spaces = 'drive',        
                        pageSize = 10,
                        fields = "nextPageToken, files(id, name, parents)",
                        pageToken = page_token
                        ).execute()
            items = response.get('files', [])
            if not items:
                print('No items found.')
            else:
                item_list += items
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        print('Found {} items.'.format(len(item_list)))
        return(item_list)

