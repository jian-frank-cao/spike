# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 20:51:39 2021

@author: bonta

File Commands (mkdir, list, move, delete, zip, unzip)
"""

## Set environment ------------------------------------------------------------
import os
import subprocess

## Define class ---------------------------------------------------------------
class FileCMD:
    """Object for file commands
    Functions:
        .CreateFolder(folder_path)
        .ListFiles(folder_path, pattern = None)

    """
    
    def _check_path(self, path):
        if not os.path.exists(path):
            print('"' + path + '" is not an valid path.')
            return(None)
        if path[-1] != '/':
            path = path + '/'
        return(path)


    def CreateFolder(self, folder_path):
        """Create a folder
        Parameters:     
           folder_path (str): path of the new folder.
        Returns:     
           None
        """ 
        if not folder_path:
            print('FOLDER_PATH is needed.')
            return(None)
        folder_path = self._check_path(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        print('Folder {} is created.'.format(folder_path))


    def ListFiles(self, folder_path, pattern = None):
        """List files
        Parameters:     
           folder_path (str): path of the target folder.
           pattern (str): a string used to filter file names.
                           Can be None.
        Returns:     
           list(str): list of file names
        """ 
        if not folder_path:
            print('FOLDER_PATH is needed.')
            return(None)
        folder_path = self._check_path(folder_path)
        if pattern is None:
            pattern = ''
        file_list = [x for x in os.listdir(folder_path) if
                     (pattern in x) and os.path.isfile(folder_path + x)]
        file_list.sort()
        return(file_list)


    def MoveFile(self, from_path, to_path, file_name):
        """Move a file from one folder to another
        Parameters:     
           from_path (str): path of the origin folder.
           to_path (str): path of the dest folder.
           file_name (str): name of the target file.
        Returns:     
           None
        """ 
        if not from_path or not to_path or not file_name:
            print('FROM_PATH, TO_PATH, and FILE_NAME are needed.')
            return(None)
        from_path = self._check_path(from_path)
        to_path = self._check_path(to_path)
        os.rename(from_path + file_name, to_path + file_name)
        print(file_name + ' is moved to ' + to_path)


    def DeleteFile(self, folder_path, file_name):
        """Delete a file from local disk
        Parameters:     
           folder_path (str): path of the target folder.
           file_name (str): name of the target file.
        Returns:     
           None
        """ 
        if not folder_path or not file_name:
            print('FOLDER_PATH and FILE_NAME are needed.')
            return(None)
        folder_path = self._check_path(folder_path)
        if not os.path.isfile(folder_path + file_name):
            print(folder_path + file_name + " doesn't exist.")
            return(None)
        os.remove(folder_path + file_name)
        print(folder_path + file_name + ' is deleted')


    def ZipFile(self, source_path, output_path,
                file_name, remove_raw = False,
                password = None, zip_type = '7z'):
        """Zip a file
        Parameters:     
           source_path (str): path of the source folder.
           output_path (str): path of the output folder.
           file_name (str): name of the target file.
           password (str): password of the 7z/zip file.
           zip_type (str): 7z/zip. Default 7z.
        Returns:     
           None
        """ 
        if not source_path or not output_path or not file_name:
            print('SOURCE_PATH, OUTPUT_PATH, and FILE_NAME are needed.')
            return(None)
        source_path = self._check_path(source_path)
        output_path = self._check_path(output_path)
        if not os.path.isfile(source_path + file_name):
            print(source_path + file_name + ' does not exist.')
            return(None)
        if not os.path.exists(output_path):
            print('Output folder {} does not exist.'.format(output_path))
            return(None)
        if '7z' in zip_type.lower():
            output_name = file_name.rsplit('.', 1)[0] + '.7z'
            command = ['7z', 'a', output_path + output_name,
                       source_path + file_name]
            if password is not None:
                command.append('-p{}'.format(password))
            subprocess.call(command)
            if remove_raw:
                self.DeleteFile(source_path, file_name)
        print(file_name + ' is zipped.')


    def UnzipFile(self, source_path, output_path,
                file_name, remove_raw = False,
                password = None, zip_type = '7z'):
        """Unzip a file
        Parameters:     
           source_path (str): path of the source folder.
           output_path (str): path of the output folder.
           file_name (str): name of the target file.
           password (str): password of the 7z/zip file.
           zip_type (str): 7z/zip. Default 7z.
        Returns:     
           None
        """ 
        if not source_path or not output_path or not file_name:
            print('SOURCE_PATH, OUTPUT_PATH, and FILE_NAME are needed.')
            return(None)
        source_path = self._check_path(source_path)
        output_path = self._check_path(output_path)
        if not os.path.isfile(source_path + file_name):
            print(source_path + file_name + ' does not exist.')
            return(None)
        if not os.path.exists(output_path):
            print('Output folder {} does not exist.'.format(output_path))
            return(None)
        if '7z' in zip_type.lower():
            command = ['7z', 'x', source_path + file_name, '-o'.format(output_path)]
            if password is not None:
                command.append('-p{}'.format(password))
            subprocess.call(command)
            if remove_raw:
                self.DeleteFile(source_path, file_name)
        print(file_name + ' is unzipped.')


