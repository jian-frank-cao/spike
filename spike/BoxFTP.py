# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 13:49:11 2021

@author: Jian Cao

Download and upload files from Box
"""

## Set environment ------------------------------------------------------------
import os
os.chdir('/home/ubuntu/twitter_monitor/coronavirus')
from ftplib import FTP_TLS, error_perm
import config

## Define class ---------------------------------------------------------------
class BoxFTP:
    def __int__(self):
        # connect to Box FTP using credentials
        # stored in config.py
        ftp = FTP_TLS(config.box_host)
        ftp.debugging = 2
        ftp.login(config.box_username, config.box_passwd)
        print('Connected to Box FTP.')
    def ListFile(self, box_path, pattern):
        self.ftp.cwd(box_path)
        file_list = self.ftp.nlst()
        file_list = [x for x in file_list if pattern in x]
        return(file_list)
    def DownloadFile(self, box_path, download_path, filename):
        self.ftp.cwd(box_path)
        retry = True
        while retry:
            retry = False
            try:
                with open(download_path + filename, 'wb') as file:
                    self.ftp.retrbinary('RETR %s' % filename, file.write)
            except error_perm as reason:
                if str(reason)[:3] != '551':
                    print(reason)
                    raise IOError
                else:
                    retry = True
                    continue
        print(download_path + filename + ' is downloaded.')
    def UploadFile(self, box_path, source_path, filename):
        self.ftp.cwd(box_path)
        retry = True
        while retry:
            retry = False
            try:
                with open(source_path + filename, 'rb') as file:
                    self.ftp.storbinary('STOR %s' % filename, file)
            except error_perm as reason:
                if str(reason)[:3] != '551':
                    print(reason)
                    raise IOError
                else:
                    retry = True
                    continue
        print(box_path + filename + ' is uploaded.')
        
## main -----------------------------------------------------------------------
if __name__ == "__main__":
    def get_box_path():
        box_path = input('Enter Box path: ')
        if box_path[0] != '/':
            box_path = '/' + box_path
        if box_path[-1] != '/':
            box_path = box_path + '/'
        return(box_path)
    
    def get_path(path_name):
        path = input('Enter %s path: ' % path_name)
        if path[-1] != '/':
            path = path + '/'
        return(path)

    obj = BoxFTP()
    i = int(input('1 - List Files,\n2 - Download File,\n3 - Upload File,\n4 - Exit.\nEnter your choice:'))
    
    if i == 1:
        box_path = get_box_path()
        file_list = obj.ListFile(box_path)
        print(file_list)
        
    elif i == 2:
        box_path = get_box_path()
        download_path = get_path('download')
        filename = input('Enter file name: ')
        obj.DownloadFile(box_path, download_path, filename)
        
    elif i == 3:
        box_path = get_box_path()
        source_path = get_path('source')
        filename = input('Enter file name: ')
        obj.UploadFile(box_path, source_path, filename)
        
    else:
        exit()
        
        
    