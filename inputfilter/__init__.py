from .lvm import parse as lvm
from .csv import csv, tsv

def __call__(src,format=None):
    if format == None:
        format = src.split('.')[-1]
    return globals()[format](src)
