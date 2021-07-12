# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 13:49:11 2021

@author: Jian Cao

Download and upload files from/to SFTP

ftplib reference:
    https://docs.python.org/3/library/ftplib.html
"""

## Set environment ------------------------------------------------------------
from ftplib import FTP_TLS, error_perm

## Define class ---------------------------------------------------------------
class ConnectSFTP:
    """Object that connects SFTP
    Functions:
        .CreateFolder(sftp_path)
        .ListFiles(sftp_path)
        .DownloadFile(sftp_path, download_path, file_name)
        .UploadFile(sftp_path, source_path, file_name)
        .DeleteFile(sftp_path, file_name)
        .MoveFile(from_sftp_path, to_sftp_path, file_name)
    """
    
    def __init__(self, sftp_host, sftp_username, sftp_passwd):
        if not sftp_host or not sftp_username or not sftp_passwd:
            print('SFTP_HOST, USERNAME, and PASSWORD are needed.')
            return(None)
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

    def _check_wd(self, path):
        try:
            resp = self.ftp.sendcmd('MLST ' + path)
            if 'Type=dir' in resp:
                return True
            else:
                return False
        except error_perm as e:
            return False


    def CreateFolder(self, sftp_path):
        """Create a folder
        Parameters:     
           sftp_path (str): path of the SFTP folder
        Returns:     
           None
        """ 
        if not sftp_path:
            print('SFTP_PATH is needed.')
            return(None)
        sftp_path = self._check_path(sftp_path, True)
        if self._check_wd(sftp_path) == False:
            self.ftp.mkd(sftp_path)
            print(sftp_path + ' is created.')


    def ListFiles(self, sftp_path):
        """List files in sftp_path
        Parameters:     
           sftp_path (str): path of the SFTP folder
        Returns:     
           list(str): list of file names
        """ 
        if not sftp_path:
            print('SFTP_PATH is needed.')
            return(None)
        sftp_path = self._check_path(sftp_path, True)
        self.ftp.cwd(sftp_path)
        file_list = self.ftp.nlst()
        file_list.sort()
        return(file_list)


    def DownloadFile(self, sftp_path, download_path, file_name):
        """Download a file from sftp to local disk
        Parameters:     
           sftp_path (str): path of the SFTP folder
           download_path (str): path of the download folder
           file_name (str): name of the target file   
        Returns:     
           None
        """ 
        if not sftp_path or not download_path or not file_name:
            print('SFTP_PATH, DOWNLOAD_PATH, and FILE_NAME are needed.')
            return(None)
        sftp_path = self._check_path(sftp_path, True)
        download_path = self._check_path(download_path, False)
        self.ftp.cwd(sftp_path)
        retry = True
        while retry:
            retry = False
            try:
                with open(download_path + file_name, 'wb') as file:
                    self.ftp.retrbinary('RETR %s' % file_name, file.write)
            except error_perm as reason:
                if str(reason)[:3] != '551':
                    print(reason)
                    raise IOError
                else:
                    retry = True
                    continue
        print(download_path + file_name + ' is downloaded.')


    def UploadFile(self, sftp_path, source_path, file_name):
        """Upload a file from local disk to SFTP
        Parameters:     
           sftp_path (str): path of the SFTP folder
           source_path (str): path of the source folder
           file_name (str): name of the target file    
        Returns:     
           None
        """ 
        if not sftp_path or not source_path or not file_name:
            print('SFTP_PATH, SOURCE_PATH, and FILE_NAME are needed.')
            return(None)
        sftp_path = self._check_path(sftp_path, True)
        source_path = self._check_path(source_path, False)
        self.ftp.cwd(sftp_path)
        retry = True
        while retry:
            retry = False
            try:
                with open(source_path + file_name, 'rb') as file:
                    self.ftp.storbinary('STOR %s' % file_name, file)
            except error_perm as reason:
                if str(reason)[:3] != '551':
                    print(reason)
                    raise IOError
                else:
                    retry = True
                    continue
        print(sftp_path + file_name + ' is uploaded.')


    def DeleteFile(self, sftp_path, file_name):
        """Delete a file from SFTP
        Parameters:     
           sftp_path (str): path of the SFTP folder
           file_name (str): name of the target file    
        Returns:     
           None
        """ 
        if not sftp_path or not file_name:
            print('SFTP_PATH and FILE_NAME are needed.')
            return(None)
        sftp_path = self._check_path(sftp_path, True)
        self.ftp.delete(sftp_path + file_name)
        print(sftp_path + file_name + ' is deleted.')


    def MoveFile(self, from_sftp_path, to_sftp_path, file_name):
        """Move a file from one SFTP path to another
        Parameters:     
           from_sftp_path (str): path of the origin SFTP folder
           to_sftp_path (str): path of the dest SFTP folder
           file_name (str): name of the target file    
        Returns:     
           None
        """ 
        if not from_sftp_path or not to_sftp_path or not file_name:
            print('FROM_SFTP_PATH, TO_SFTP_PATH and FILE_NAME are needed.')
            return(None)
        from_sftp_path = self._check_path(from_sftp_path, True)
        to_sftp_path = self._check_path(to_sftp_path, True)
        self.ftp.rename(from_sftp_path + file_name,
                        to_sftp_path + file_name)
        print(file_name + ' is movded to ' + to_sftp_path)

        
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
        file_name = input('Enter file name: ')
        obj.DownloadFile(sftp_path, download_path, file_name)
        
    elif i == 3:
        sftp_path = input('Enter SFTP path: ')
        sftp_path = obj._check_path(sftp_path, True)
        source_path = input('Enter source path: ')
        source_path = obj._check_path(source_path, False)
        file_name = input('Enter file name: ')
        obj.UploadFile(sftp_path, source_path, file_name)
        
    else:
        exit()
        
        
    