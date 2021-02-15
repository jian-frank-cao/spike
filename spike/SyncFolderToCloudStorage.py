# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 20:05:19 2021

@author: Jian Cao

Sync Folder to Google Cloud Storage
"""

# Setup
import spike
import pandas as pd
from datetime import datetime, timedelta
import time

def SyncFolderToCloudStorage(source_path,
                            zip_path,
                            token_path,
                            storage_bucket,
                            time_pos,
                            remove_raw = True,
                            password = None,
                            bucket_folder = None,
                            pattern = '',
                            marker = None,
                            time_format = '%Y-%m-%d-%H-%M-%S',
                            delete_after_days = 7,
                            wait_retry = 5,
                            wait_next = 900):
    if (not source_path or not zip_path or not token_path or
        not storage_bucket or not time_pos):
        raise ValueError('SOURCE_PATH, TOKEN_PATH, ZIP_PATH, ' +
              'STORAGE_BUCKET, and TIME_POS are needed')
    
    while True:
        retry = False
        # connect Cloud Storage
        storage = spike.ConnectGoogleCloudStorage(token_path)
        
        # prepare File CMD module
        file_cmd = spike.FileCMD()
        
        # zip files
        file_cmd.ZipFolder(source_path,
                           zip_path,
                           pattern = pattern,
                           remove_raw = remove_raw,
                           password = password)
        
        # list files
        file_list = file_cmd.ListFiles(zip_path, '.7z')
        
        # sort time
        if not (len(time_pos) == 2 and
                time_pos[0] < time_pos[1] and
                time_pos[1] < len(file_list[0].rsplit('.', 1)[0])):
            raise ValueError('TIME_POS should be the location ' + 
                  '[start, end] of the time substring.')
            
        file_time = [datetime.strptime(x[time_pos[0]:time_pos[1]],
                                       time_format) for x in file_list]
        file_df = pd.DataFrame({'file_name': file_list, 'time': file_time})
        file_df = file_df.sort_values(by = 'time',
                                      ascending = True).reset_index()
        
        # specify files will be uploaded/deleted
        file_upload_list = file_df['file_name'].tolist()
        if marker:
            upload_cutoff = datetime.strptime(marker[time_pos[0]:time_pos[1]],
                                       time_format)
            file_upload_list = file_df[file_df['time'] >
                                       upload_cutoff]['file_name'].tolist()
        
        delete_cutoff = datetime.now() - timedelta(days = delete_after_days)
        file_delete_list = file_df[file_df['time'] <
                                   delete_cutoff]['file_name'].tolist()
        
        # upload files
        for file_name in file_upload_list:
            try:
                storage.UploadFile(storage_bucket,
                                   zip_path,
                                   file_name,
                                   bucket_folder)
                marker = file_name
            except:
                print('Failed uploading ' + file_name)
                retry = True
                continue
        
        # delete old files
        for file_name in file_delete_list:
            file_cmd.DeleteFile(source_path, file_name)
        
        # finish
        if retry:
            print('Re-trying...')
            time.sleep(wait_retry)
        else:
            print('Folder {' + source_path +
                  '} have been synchronized to ' +
                  'Cloud Storage bucket {' + storage_bucket +
                  '}, folder {' + bucket_folder + '}.')
            print('Waiting for the next update...')
            time.sleep(wait_next)
        
            
            
    
    