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
# from googleapiclient.errors import HttpError
import shutil

## Define class ---------------------------------------------------------------
class ConnectGoogleDrive:
    """Object that connects Google Drive
    Functions:
        .CreateFolder(parents, folder_name)
        .ListItems(item_name, parents)
        .DownloadFile(download_path, file_name, file_id)
        .UploadFile(source_path, parents, file_name)
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


    def CreateFolder(self, parents, folder_name):
        """Create a folder
        Parameters:     
           parents (str): ID of the parent folder 
           folder_name (str): name of the new folder
        Returns:     
           dict: {id, name, parents}
        """ 
        # prepare metadata
        file_metadata = {
            'name': folder_name,
            'parents': [parents],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        # create folder
        response = self.service.files().create(body=file_metadata,
                            fields='id, name, parents').execute()
        print('Folder {} has been created.'.format(folder_name))
        return(response)


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
        # prepare query and item holder
        page_token = None
        item_list = []
        if item_name and parents:
            print('Please specify either ITEM_NAME or PARENTS, not both...')
            return None
        elif item_name:
            query = "name='{}'".format(item_name)
        else:
            query = "'{}' in parents".format(parents)
        # list files
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


    def DownloadFile(self, download_path, file_name, file_id):
        """Download file from Google Drive to local disk
        Parameters:     
           download_path (str): path of the download folder
           file_name (str): name of the target file   
           file_id (str): ID of the target file
        Returns:     
           None
        """ 
        if not download_path or not file_name or not file_id:
            print('DOWNLOAD_PATH, FILE_NAME, and FILE_ID are needed...')
            return(None)
        download_path = self._check_path(download_path)
        # download file
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        fh.seek(0)
        # Write the received data to the file
        with open(download_path + file_name, 'wb') as file: 
            shutil.copyfileobj(fh, file)
        print(download_path + file_name + ' is downloaded.')
        
        
    def UploadFile(self, source_path, parents, file_name):
        """Upload file from local disk to Google Drive
        Parameters:     
           source_path (str): path of the source folder
           parents (str): ID of the target GD folder
           file_name (str): name of the target file   
        Returns:     
           None
        """ 
        if not source_path or not parents or not file_name:
            print('SOURCE_PATH, PARENTS, and FILE_NAME are needed...')
            return(None)
        source_path = self._check_path(source_path)
        # prepare metadata
        file_metadata = {
            'name': file_name,
            'parents': [parents]
        }
        media = MediaFileUpload(source_path + file_name)
        # upload file
        response = self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id, name, parents'
                        ).execute()
        print('{} {{}} is uploaded.'.format(response['name'],
                                              response['id']))
        
        
        
        