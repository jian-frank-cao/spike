# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 20:05:19 2021

@author: Jian Cao

Sync Files to Google Cloud Storage
"""

# Setup
import spike

def SyncFilesToCloudStorage(source_path,
                            storage_token,
                            storage_bucket,
                            bucket_folder,
                            marker = None,
                            zip_file = True):
    # connect Cloud Storage
    storage = spike.ConnectGoogleCloudStorage(storage_token)
    
    # prepare File CMD module
    file_cmd = spike.FileCMD()
    
    # list files