import hashlib

def hash(fd):
    '''returns hashlib.sha256 object of everything that could be read from fd
    tries to seek to 0 before reading, also reopen binary'''

    if 'w' in fd.mode:
        raise IOError('%fd is open for writing, exciting'%str(fd))
    if not 'b' in fd.mode:
        fd = open(fd.name,'rb')
    try:
        fd.seek(0)
    except AttributeError:
        pass

    sha = hashlib.sha256()
    for chunk in iter(lambda: fd.read(2**14),b''):
        sha.update(chunk)
    return sha
