# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:53:22 2021

@author: Jian Cao

Download and upload files from/to Google Cloud Storage
"""

## Set environment ------------------------------------------------------------
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError

## Define class ---------------------------------------------------------------
class ConnectGoogleCloudStorage:
    """Object that connects Google Cloud Storage
    Functions:
        .ListFiles(bucket_name, bucket_folder = None)
        .DownloadFile(bucket_name, download_path,
                     file_name, bucket_folder = None)
        .UploadFile(bucket_name, source_path,
                   file_name, bucket_folder = None)
        .DeleteFile(bucket_name, file_name, bucket_folder = None)
        .MoveFile(from_bucket_name, from_bucket_folder,
                 to_bucket_name, to_bucket_folder, file_name)
    """
    
    def __init__(self, token_path):
        if not token_path:
            print('TOKEN_PATH is needed.')
            return(None)
        try:
            # windows might get error:
            # 'ClientOptions' object has no attribute 'credentials_file'
            self.client = storage.Client.from_service_account_json(token_path)
        except DefaultCredentialsError as dce:
            print(dce)
            return(None)


    def _check_path(self, path):
        if path[-1] != '/':
            path = path + '/'
        return(path)


    def ListFiles(self, bucket_name, bucket_folder = None):
        """List files
        Parameters:     
           bucket_name (str): name of the storage bucket.
           bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           list(dict): list of {prefix, name}
        """ 
        if not bucket_name:
            print('BUCKET_NAME is needed.')
            return(None)
        blobs = self.client.list_blobs(bucket_name, prefix = bucket_folder)
        blob_list = [blob.name for blob in blobs]
        blob_list.sort()
        item_list = [{'bucket_folder': x.rsplit('/', 1)[0] + '/',
                      'name': x.rsplit('/', 1)[1]} for x in blob_list]
        return(item_list)


    def DownloadFile(self, bucket_name, download_path,
                     file_name, bucket_folder = None):
        """Download a file from Cloud Storage to local disk
        Parameters:  
            bucket_name (str): name of the storage bucket.
            download_path (str): path of the download folder.
            file_name (str): name of the target file.
            bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           None
        """ 
        if not bucket_name or not download_path or not file_name:
            print('BUCKET_NAME, DOWNLOAD_PATH, FILE_NAME are needed.')
            return(None)
        download_path = self._check_path(download_path)
        if bucket_folder:
            bucket_folder = self._check_path(bucket_folder)
        else:
            bucket_folder = ''
        # download file
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(bucket_folder + file_name)
        blob.download_to_filename(download_path + file_name)
        print(download_path + file_name + ' is downloaded.')


    def UploadFile(self, bucket_name, source_path,
                   file_name, bucket_folder = None):
        """Upload a file from local disk to Cloud Storage
        Parameters:  
            bucket_name (str): name of the storage bucket.
            source_path (str): path of the source folder.
            file_name (str): name of the target file.
            bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           None
        """ 
        if not bucket_name or not source_path or not file_name:
            print('BUCKET_NAME, SOURCE_PATH, FILE_NAME are needed.')
            return(None)
        source_path = self._check_path(source_path)
        if bucket_folder:
            bucket_folder = self._check_path(bucket_folder)
        else:
            bucket_folder = ''
        # upload file
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(bucket_folder + file_name)
        blob.upload_from_filename(source_path + file_name)
        print(bucket_folder + file_name + ' is uploaded.')


    def DeleteFile(self, bucket_name, file_name, bucket_folder = None):
        """Delete a file from Cloud Storage
        Parameters:  
            bucket_name (str): name of the storage bucket.
            file_name (str): name of the target file.
            bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           None
        """ 
        if not bucket_name or not file_name:
            print('BUCKET_NAME, FILE_NAME are needed.')
            return(None)
        if bucket_folder:
            bucket_folder = self._check_path(bucket_folder)
        else:
            bucket_folder = ''
        # delete file
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(bucket_folder + file_name)
        blob.delete()
        print(bucket_folder + file_name + ' is deleted.')


    def MoveFile(self, from_bucket_name, from_bucket_folder,
                 to_bucket_name, to_bucket_folder, file_name):
        """Move a file from one Storage bucket/folder to another
        Parameters:  
            from_bucket_name (str): name of the origin bucket.
            from_bucket_folder (str): path of the origin bucket folder.
                                        Can be None.
            to_bucket_name (str): name of the dest bucket.
            to_bucket_folder (str): path of the dest bucket folder.
                                        Can be None.
            file_name (str): name of the target file.
        Returns:     
           None
        """
        if not from_bucket_name or not to_bucket_name or not file_name:
            print('ORIGIN/DEST_BUCKET_NAME, FILE_NAME are needed.')
            return(None)
        if from_bucket_folder:
            from_bucket_folder = self._check_path(from_bucket_folder)
        else:
            from_bucket_folder = ''
        if to_bucket_folder:
            to_bucket_folder = self._check_path(to_bucket_folder)
        else:
            to_bucket_folder = ''
        # move file
        origin_bucket = self.client.bucket(from_bucket_name)
        origin_blob = origin_bucket.blob(from_bucket_folder + file_name)
        dest_bucket = self.client.bucket(to_bucket_name)
        dest_blob = dest_bucket.blob(to_bucket_folder + file_name)
        (token, _, __) = dest_blob.rewrite(origin_blob)
        while token is not None:
            (token, _, __) = dest_blob.rewrite(origin_blob, token = token)
        if token is not None:
            print("Moving didn't finish.")
            return(None)
        origin_blob.delete()
        print(file_name + ' is moved to ' +
              to_bucket_name + '/' + to_bucket_folder)
    
