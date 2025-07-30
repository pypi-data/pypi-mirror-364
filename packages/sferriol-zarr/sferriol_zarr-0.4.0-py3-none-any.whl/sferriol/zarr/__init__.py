import os
import tarfile
import uuid

import zarr

from .fsspec_ import create_store

class TarStore(zarr._storage.store.Store):
    def __init__(self, path):
        path = os.path.abspath(path)
        self.path = path
        self.tf = tarfile.open(path)
        self.prefix = os.path.basename(path).replace('.tar', '') + '/'

    def __contains__(self, item: str):
        item = os.path.join(self.prefix, item)
        return item in self.tf.getnames()

    def __delitem__(self, item: str):
        raise NotImplementedError('TarStore is a read-only store')
    
    def __getitem__(self, item: str):
        item = os.path.join(self.prefix, item)
        return self.tf.extractfile(item).read()

    def __iter__(self):
        return self.keys()

    def __len__(self) -> int:
        return sum(1 for _ in self.keys())

    def __setitem__(self, item: str, value):
        raise NotImplementedError('TarStore is a read-only store')
    
    def close(self):
        """Closes the underlying tar file."""
        self.tf.close()

    def getsize(self, path=None):
        file_path = os.path.join(self.prefix, path)
        tar_path = zarr.util.normalize_storage_path(file_path)
        tar_elt = self.tf.getmember(tar_path)

        if tar_elt.isfile():
            return tar_elt.size
        elif tar_elt.isdir():
            size = 0
            childs = [
                k for k in self.tf.getnames() if k.startswith(tar_path + '/')
            ]
            for child in childs:
                elt = self.tf.getmember(child)
                if elt.isfile():
                    size += elt.size
            return size
        else:
            return 0

    def keys(self):
        for m in self.tf:
            if m.isfile():
                yield m.name.replace(self.prefix, '')

    def listdir(self, path=None):
        tar_path = zarr.util.normalize_storage_path(path)
        if tar_path:
            tar_path = tar_path + '/'
        tar_path_len = len(tar_path)
        s = set([
            k[tar_path_len:].split('/', 1)[0] for k in self.keys()
            if k.startswith(tar_path)
        ])
        return list(s)


def create_tar(src_path, dest_dir=None, use_temp_file=False):
    """Create a tar archive of source. The tar file name is the source path name with '.tar' extension.
    Instead of building tar file in place, a temporary hidden file can be used. At the end, it is renamed to the tar file name.

    Parameters
    ----------
    src_path -- Source path 
    dest_dir -- Destination directory path (create it if not exists). If None, source path directory is used.
    use_temp_file -- Use temporary tar file

    Returns
    -------
    New tar file name
    """
    src_fname = os.path.basename(src_path)
    src_path = os.path.normpath(src_path)
    tar_fname = src_fname + '.tar'
    if dest_dir is None:
        dest_dir = os.path.dirname(src_path)
    elif not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    tar_fpath = os.path.join(dest_dir, tar_fname)
    if not use_temp_file:
        tmp_fpath = tar_fpath
    else:
        suffix = str(uuid.uuid4()).split('-')[0]
        tmp_fpath = f'{tar_fpath}.{suffix}'
    with tarfile.open(tmp_fpath, "w") as tar:
        tar.add(name=src_path, arcname=src_fname)
    if use_temp_file:
        os.rename(tmp_fpath, tar_fpath)
    return tar_fpath
