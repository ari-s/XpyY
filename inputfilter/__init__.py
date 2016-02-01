from .lvm import parse as lvm

def __call__(src,format=None):
    if format == None:
        format = src.split('.')[-1]
    return globals()[format](src)
