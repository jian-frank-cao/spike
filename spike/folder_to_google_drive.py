# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 09:38:58 2021

@author: Jian Cao

Move files from local folder to Google Drive
"""

import spike

def folder_to_google_drive(token_path, source_path, gd_folder):
    """Move files from local folder to Google Drive
    Parameters: 
        token_path (str): path to the GD token.
        source_path (str): path to the source folder.
        folder_name (str): name of the GD folder.
    Returns:     
       None
    """ 
    google_drive = spike.ConnectGoogleDrive(token_path)
    file_cmd = spike.FileCMD()
    file_list = file_cmd.ListFiles(source_path)
    print('Uploading...')
    print('\n'.join(file_list))
    
    item_list = google_drive.ListItems(gd_folder, None)
    folder_id = item_list[0]['id']
    
    for file_name in file_list:
        google_drive.UploadFile(source_path, folder_id, file_name)