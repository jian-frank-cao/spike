# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 10:50:10 2021

@author: Jian Cao

Zip all Files of a Folder
"""

import spike

def ZipFolder(source_path,
              output_path,
              pattern = '',
              remove_raw = False,
              password = None):
    
    # file CMD module
    file_cmd = spike.FileCMD()
    
    # list files
    file_list = file_cmd.ListFiles(source_path, pattern)
    
    # check if there are files need to be zipped
    if len(file_list) == 0:
        print('No files in folder {{}} need to be zipped.'.format(source_path))
        return(None)
    
    # zip files
    for file_name in file_list:
        file_cmd.ZipFile(source_path,
                         output_path,
                         file_name,
                         remove_raw = remove_raw,
                         password = password)
    
    # finish
    print('Files in folder {{}} are zipped.'.format(source_path))
    return(None)

