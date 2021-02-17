# spike
Python toolbox for:

1. launching Twitter Stream/REST monitors*.
2. managing data files in Google Drive, Goolge Cloud Storage, SFTP, and local system.

*A technical report for the Twitter monitors: [Reliable and Efficient Long-Term Social Media Monitoring](https://arxiv.org/pdf/2005.02442.pdf)

## Installation
```ruby
pip3 install git+https://github.com/jian-frank-cao/spike.git@main
```

## Module: TwitterMonitor
- ConnectTwitterAPI
- SyncFolderToCloudStorage

### TwitterMonitor.ConnectTwitterAPI
```ruby
from spike.TwitterMonitor import ConnectTwitterAPI
twitter_api = ConnectTwitterAPI(consumer_key,
                                consumer_secret,
                                access_token_key,
                                access_token_secret)
```

## Module: DataTools
- ConnectGoogleDrive
- ConnectGoogleCloudStorage
- ConnectSFTP
- FileCMD
- DownloadFolderFromGD
- UploadFolderToGD

### DataTools.ConnectGoogleDrive
```ruby
"""Object that connects Google Drive"""
from spike.DataTools import ConnectGoogleDrive
drive = ConnectGoogleDrive(token_path)
```
```ruby
Functions:
    .CreateFolder(parents, folder_name)
        """Create a folder
        Parameters:     
           parents (str): ID of the parent folder
           folder_name (str): name of the new folder
        Returns:     
           dict: {id, name, parents}
        """ 
        
    .ListItems(item_name, parents)
        """List items (file/folder) by name or parents 
        Parameters:     
           item_name (str): name of file/folder. Can be None.
           parents (str): target folder ID. Can be None.
        Returns:     
           list(dict): list of {id, name, parents}
        """ 
        
    .DownloadFile(download_path, file_name, file_id)
        """Download a file from Google Drive to local disk
        Parameters:     
           download_path (str): path of the download folder
           file_name (str): name of the target file   
           file_id (str): ID of the target file
        Returns:     
           None
        """ 
        
    .UploadFile(source_path, parents, file_name)
        """Upload a file from local disk to Google Drive
        Parameters:     
           source_path (str): path of the source folder
           parents (str): ID of the target GD folder
           file_name (str): name of the target file   
        Returns:     
           None
        """ 
        
    .DeleteFile(file_id)
        """Delete a file from GD
        Parameters:   
            file_id (str): ID of the target file
        Returns:     
           None
        """ 
        
    .MoveFile(file_id, new_parents)
        """Move a file from one GD folder to another
        Parameters:   
            file_id (str): ID of the target file
            new_parents (str): ID of the destination GD folder
        Returns:     
           None
        """ 
```

### DataTools.ConnectGoogleCloudStorage
```ruby
"""Object that connects Google Cloud Storage"""
from spike.DataTools import ConnectGoogleCloudStorage
storage = ConnectGoogleCloudStorage(token_path)
```
```ruby
Functions:
    .ListFiles(bucket_name, bucket_folder = None)
        """List files
        Parameters:     
           bucket_name (str): name of the storage bucket.
           bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           list(dict): list of {prefix, name}
        """ 
        
    .DownloadFile(bucket_name, download_path,
                 file_name, bucket_folder = None)
        """Download a file from Cloud Storage to local disk
        Parameters:  
            bucket_name (str): name of the storage bucket.
            download_path (str): path of the download folder.
            file_name (str): name of the target file.
            bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           None
        """ 
        
    .UploadFile(bucket_name, source_path,
               file_name, bucket_folder = None)
        """Upload a file from local disk to Cloud Storage
        Parameters:  
            bucket_name (str): name of the storage bucket.
            source_path (str): path of the source folder.
            file_name (str): name of the target file.
            bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           None
        """ 
        
    .DeleteFile(bucket_name, file_name, bucket_folder = None)
        """Delete a file from Cloud Storage
        Parameters:  
            bucket_name (str): name of the storage bucket.
            file_name (str): name of the target file.
            bucket_folder (str): path of the bucket folder. Can be None.
        Returns:     
           None
        """ 
        
    .MoveFile(from_bucket_name, from_bucket_folder,
             to_bucket_name, to_bucket_folder, file_name)
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
```

### DataTools.ConnectSFTP
```ruby
"""Object that connects SFTP"""
from spike.DataTools import ConnectSFTP
sftp = ConnectSFTP(token_path)
```
```ruby
Functions:
    .CreateFolder(sftp_path)
        """Create a folder
        Parameters:     
           sftp_path (str): path of the SFTP folder
        Returns:     
           None
        """ 
        
    .ListFiles(sftp_path)
        """List files in sftp_path
        Parameters:     
           sftp_path (str): path of the SFTP folder
        Returns:     
           list(str): list of file names
        """ 
        
    .DownloadFile(sftp_path, download_path, file_name)
        """Download a file from sftp to local disk
        Parameters:     
           sftp_path (str): path of the SFTP folder
           download_path (str): path of the download folder
           file_name (str): name of the target file   
        Returns:     
           None
        """ 
        
    .UploadFile(sftp_path, source_path, file_name)
        """Upload a file from local disk to SFTP
        Parameters:     
           sftp_path (str): path of the SFTP folder
           source_path (str): path of the source folder
           file_name (str): name of the target file    
        Returns:     
           None
        """ 
        
    .DeleteFile(sftp_path, file_name)
        """Delete a file from SFTP
        Parameters:     
           sftp_path (str): path of the SFTP folder
           file_name (str): name of the target file    
        Returns:     
           None
        """ 
        
    .MoveFile(from_sftp_path, to_sftp_path, file_name)
        """Move a file from one SFTP path to another
        Parameters:     
           from_sftp_path (str): path of the origin SFTP folder
           to_sftp_path (str): path of the dest SFTP folder
           file_name (str): name of the target file    
        Returns:     
           None
        """ 
```

### DataTools.FileCMD
```ruby
"""Object for file commands"""
from spike.DataTools import FileCMD
file_cmd = FileCMD()
```
```ruby
Functions:
    .CreateFolder(folder_path)
        """Create a folder
        Parameters:     
           folder_path (str): path of the new folder.
        Returns:     
           None
        """ 
        
    .ListFiles(folder_path, pattern = None)
        """List files
        Parameters:     
           folder_path (str): path of the target folder.
           pattern (str): a string used to filter file names.
                           Can be None.
        Returns:     
           list(str): list of file names
        """ 
        
    .MoveFile(self, from_path, to_path, file_name)
        """Move a file from one folder to another
        Parameters:     
           from_path (str): path of the origin folder.
           to_path (str): path of the dest folder.
           file_name (str): name of the target file.
        Returns:     
           None
        """ 
        
    .DeleteFile(self, folder_path, file_name)
        """Delete a file from local disk
        Parameters:     
           folder_path (str): path of the target folder.
           file_name (str): name of the target file.
        Returns:     
           None
        """ 
        
    .ZipFile(self, source_path, output_path,
            file_name, remove_raw = False,
            password = None, zip_type = '7z')
        """Zip a file
        Parameters:     
           source_path (str): path of the source folder.
           output_path (str): path of the output folder.
           file_name (str): name of the target file.
           remove_raw (bool): remove the raw file or not.
           password (str): password of the 7z/zip file.
           zip_type (str): 7z/zip. currently supports 7z.
        Returns:     
           None
        """ 
        
    .ZipFolder(self, source_path, output_path,
          pattern = '', remove_raw = False,
          password = None, zip_type = '7z')
        """Zip files in a folder
        Parameters:     
           source_path (str): path of the source folder.
           output_path (str): path of the output folder.
           pattern (str): used to filter files.
           remove_raw (bool): remove the raw files or not.
           password (str): password of the 7z/zip file.
           zip_type (str): 7z/zip. currently supports 7z.
        Returns:     
           None
        """ 
```

### DataTools.DownloadFolderFromGD
```ruby
"""Function that moves files from local folder to Google Drive"""
from spike.DataTools import DownloadFolderFromGD
DownloadFolderFromGD(token_path, download_path, gd_folder)
    """
    Parameters: 
        token_path (str): path to the GD token.
        download_path (str): path to the download folder.
        folder_name (str): name of the GD folder.
    Returns:     
       None
    """ 
```

### DataTools.UploadFolderToGD
```ruby
"""Function that moves files from local folder to Google Drive"""
from spike.DataTools import UploadFolderToGD
UploadFolderToGD(token_path, source_path, gd_folder)
    """
    Parameters: 
        token_path (str): path to the GD token.
        source_path (str): path to the source folder.
        folder_name (str): name of the GD folder.
    Returns:     
       None
    """ 
```
