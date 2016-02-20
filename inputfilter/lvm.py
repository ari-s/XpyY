#!/usr/bin/python3

import numpy,hashlib,appdirs,os.path,os
from .. import helpers
import re

cacheDir = appdirs.user_cache_dir('XpyY',appauthor='Arian Sanusi')
try: os.mkdir(cacheDir)
except FileExistsError: pass
digitre=re.compile(rb'\d')

def parse(infile):
    ''' returns an array of the given LVMs data
    caches data for big files >1MB'''
    try: infile.read
    except AttributeError: infile = open(infile,'rb')

    try: fsize = os.stat(infile.fileno()).st_size
    except OSError: pass
    else:
        if fsize > 1e6:
            dataHash = helpers.hash(infile)
            cache = os.path.join(cacheDir,dataHash.hexdigest())
            try:
                return numpy.load(cache)
            except FileNotFoundError:
                print('uncached')
                pass

    # will not be reached if loaded from cache
    infile.seek(0)
    chanCount=0
    for line in infile:
        try: chanCount = int(re.search(b'Channels\t(\d+)',line).group(1))
        except AttributeError: chanCount = max((chanCount, len(line.split(b'\t'))-1))
        else: break
    infile.seek(0) # we may have consumed the whole infile befor for chanCount
    result = []
    for line in infile:
        if digitre.match(line):
            result.extend(map(float,line.split(b'\t')))
    result = numpy.array(result)
    #import pdb; pdb.set_trace()
    result.shape = (-1,chanCount+1) # WTF, why does assigning change shape
    result = result.transpose()
    try:numpy.save(open(cache,'wb'),result)
    except NameError: pass
    return result
