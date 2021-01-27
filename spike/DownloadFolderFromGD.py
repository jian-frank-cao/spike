# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 10:54:44 2021

@author: Jian Cao

Move files from Google Drive folder to local folder
"""
token_path = '/home/jccit_caltech_edu/tokens/token.pickle'
import spike

def DownloadFolderFromGD(token_path, download_path, gd_folder):
    """Move files from local folder to Google Drive
    Parameters: 
        token_path (str): path to the GD token.
        download_path (str): path to the download folder.
        folder_name (str): name of the GD folder.
    Returns:     
       None
    """ 
    google_drive = spike.ConnectGoogleDrive(token_path)
    item_list = google_drive.ListItems(gd_folder, None)
    if len(item_list) > 1:
        print('Found multiple GD folders, Please rename the folder.')
        return(None)
    folder_id = item_list[0]['id']
    item_list = google_drive.ListItems(None, folder_id)
    if len(item_list) == 0:
        print('There is no files to download. Exiting...')
        return(None)
    file_list = [x['name'] for x in item_list]
    print('Download List:')
    print('\n'.join(file_list))
    
    for item in item_list:
        google_drive.DownloadFile(download_path, item['name'], item['id'])