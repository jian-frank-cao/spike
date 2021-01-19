# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 13:49:11 2021

@author: Jian Cao

Download and upload files from Box
"""

## Set environment ------------------------------------------------------------
import os
from ftplib import FTP_TLS, error_perm

## Define class ---------------------------------------------------------------
class BoxFTP:
    """Object that connects Box FTP
    Functions:
        .ListFile(box_path, pattern)
        .DownloadFile(box_path, download_path, filename)
        .UploadFile(box_path, source_path, filename)
    Parameters:     
       box_path (str): path of the Box folder
       pattern (str): string used in filtering files
       download_path (str): path of the download folder
       source_path (str): path of the source folder
       filename (str): name of the target file   
    Returns:     
       int: sum of x and y
    """
    
    def __init__(self, box_host, box_username, box_passwd):
        self.ftp = FTP_TLS(box_host)
        self.ftp.debugging = 2
        self.ftp.login(box_username, box_passwd)
        print('Connected to Box FTP.')


    def _check_path(self, path, is_box_path):
        if path[-1] != '/':
            path = path + '/'
        if not is_box_path:
            return(path)
        if path[0] != '/':
            path = '/' + path
        return(path)


    def ListFiles(self, box_path, pattern):
        """List files in box_path
        Parameters:     
           box_path (str): path of the Box folder
           pattern (str): string used in filtering files 
        Returns:     
           list(str): list of file names
        """ 
        box_path = self._check_path(box_path, True)
        self.ftp.cwd(box_path)
        file_list = self.ftp.nlst()
        file_list = [x for x in file_list if pattern in x]
        return(file_list)


    def DownloadFile(self, box_path, download_path, filename):
        """Download file from box to local disk
        Parameters:     
           box_path (str): path of the Box folder
           download_path (str): path of the download folder
           filename (str): name of the target file   
        Returns:     
           None
        """ 
        box_path = self._check_path(box_path, True)
        download_path = self._check_path(download_path, False)
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
        """Upload file from local disk to Box
        Parameters:     
           box_path (str): path of the Box folder
           source_path (str): path of the source folder
           filename (str): name of the target file    
        Returns:     
           None
        """ 
        box_path = self._check_path(box_path, True)
        source_path = self._check_path(source_path, False)
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
        box_path = input('Enter Box path: ')
        box_path = obj._check_path(box_path, True)
        file_list = obj.ListFiles(box_path)
        print(file_list)
        
    elif i == 2:
        box_path = input('Enter Box path: ')
        box_path = obj._check_path(box_path, True)
        download_path = input('Enter download path: ')
        download_path = obj._check_path(download_path, False)
        filename = input('Enter file name: ')
        obj.DownloadFile(box_path, download_path, filename)
        
    elif i == 3:
        box_path = input('Enter Box path: ')
        box_path = obj._check_path(box_path, True)
        source_path = input('Enter source path: ')
        source_path = obj._check_path(source_path, False)
        filename = input('Enter file name: ')
        obj.UploadFile(box_path, source_path, filename)
        
    else:
        exit()
        
        
    