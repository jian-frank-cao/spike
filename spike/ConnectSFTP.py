# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 13:49:11 2021

@author: Jian Cao

Download and upload files from SFTP
"""

## Set environment ------------------------------------------------------------
import os
from ftplib import FTP_TLS, error_perm

## Define class ---------------------------------------------------------------
class ConnectSFTP:
    """Object that connects SFTP
    Functions:
        .ListFile(sftp_path, pattern)
        .DownloadFile(sftp_path, download_path, filename)
        .UploadFile(sftp_path, source_path, filename)
    Parameters:     
       sftp_path (str): path of the SFTP folder
       pattern (str): string used in filtering files
       download_path (str): path of the download folder
       source_path (str): path of the source folder
       filename (str): name of the target file   
    Returns:     
       int: sum of x and y
    """
    
    def __init__(self, sftp_host, sftp_username, sftp_passwd):
        self.ftp = FTP_TLS(sftp_host)
        self.ftp.debugging = 2
        self.ftp.login(sftp_username, sftp_passwd)
        print('Connected to SFTP.')


    def _check_path(self, path, is_sftp_path):
        if path[-1] != '/':
            path = path + '/'
        if not is_sftp_path:
            return(path)
        if path[0] != '/':
            path = '/' + path
        return(path)


    def ListFiles(self, sftp_path, pattern):
        """List files in sftp_path
        Parameters:     
           sftp_path (str): path of the SFTP folder
           pattern (str): string used in filtering files 
        Returns:     
           list(str): list of file names
        """ 
        sftp_path = self._check_path(sftp_path, True)
        self.ftp.cwd(sftp_path)
        file_list = self.ftp.nlst()
        file_list = [x for x in file_list if pattern in x]
        return(file_list)


    def DownloadFile(self, sftp_path, download_path, filename):
        """Download file from sftp to local disk
        Parameters:     
           sftp_path (str): path of the SFTP folder
           download_path (str): path of the download folder
           filename (str): name of the target file   
        Returns:     
           None
        """ 
        sftp_path = self._check_path(sftp_path, True)
        download_path = self._check_path(download_path, False)
        self.ftp.cwd(sftp_path)
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


    def UploadFile(self, sftp_path, source_path, filename):
        """Upload file from local disk to SFTP
        Parameters:     
           sftp_path (str): path of the SFTP folder
           source_path (str): path of the source folder
           filename (str): name of the target file    
        Returns:     
           None
        """ 
        sftp_path = self._check_path(sftp_path, True)
        source_path = self._check_path(source_path, False)
        self.ftp.cwd(sftp_path)
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
        print(sftp_path + filename + ' is uploaded.')

        
## main -----------------------------------------------------------------------
if __name__ == "__main__":

    obj = ConnectSFTP()
    i = int(input('1 - List Files,\n2 - Download File,\n3 - Upload File,\n4 - Exit.\nEnter your choice:'))
    
    if i == 1:
        sftp_path = input('Enter SFTP path: ')
        sftp_path = obj._check_path(sftp_path, True)
        file_list = obj.ListFiles(sftp_path)
        print(file_list)
        
    elif i == 2:
        sftp_path = input('Enter SFTP path: ')
        sftp_path = obj._check_path(sftp_path, True)
        download_path = input('Enter download path: ')
        download_path = obj._check_path(download_path, False)
        filename = input('Enter file name: ')
        obj.DownloadFile(sftp_path, download_path, filename)
        
    elif i == 3:
        sftp_path = input('Enter SFTP path: ')
        sftp_path = obj._check_path(sftp_path, True)
        source_path = input('Enter source path: ')
        source_path = obj._check_path(source_path, False)
        filename = input('Enter file name: ')
        obj.UploadFile(sftp_path, source_path, filename)
        
    else:
        exit()
        
        
    