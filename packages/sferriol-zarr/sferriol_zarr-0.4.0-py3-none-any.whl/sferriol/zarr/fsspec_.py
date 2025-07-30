import os
import urllib.parse

import fsspec
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.implementations.tar import TarFileSystem
from fsspec.implementations.zip import ZipFileSystem
try:
    import fsspec_xrootd
except ModuleNotFoundError:
    pass
import zarr

def create_store(url: str):
    '''Parse the URL and return the corresponding Zarr store

    For the moment, the store is only in read mode

    Supports the following URL formats:
    local path: url='/..../my_data[.zarr, .zarr.tar, .zarr.zip]
    xrootd path: url='root://host:port///..../my_data[.zarr, .zarr.tar, .zarr.zip]
    '''
    if url.endswith('.tar'):
        return create_tar_store(url)
    if url.endswith('.zarr'):
        return create_zarr_store(url)
    if url.endswith('.zip'):
        return create_zip_store(url)
    
def create_zarr_store(url):
    fs = DirFileSystem(url)
    store = zarr.storage.FSStore(url='', fs = fs, mode="r")
    return store

def create_zip_store(url):
    fs = ZipFileSystem(url)
    store = zarr.storage.FSStore(url='', fs = fs, mode="r")
    return store


def create_tar_store(url):
    prefix = os.path.basename(url).replace('.tar', '')
    fs = TarFileSystem(url)
    fs = DirFileSystem(path=prefix, fs=fs)
    store = zarr.storage.FSStore(url='', fs = fs, mode="r")
    return store
