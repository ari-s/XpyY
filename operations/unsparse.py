import numpy
from . import strptime,dmap
def unsparse(data, relativeTo=0, dtype=float,relFunc=1, otherFunc=1):
    '''from a sparse data set (i.e. one which has one column with all entries present,
    others that are relative to the non-sparse one (like time->measuremnt maps))
    create a list [r,d[1],r,d[2],...]'''

    rel = dmap([data[0]],[relFunc])[0]
    sparseColCount = (len(data)-1)*2
    unsparsed = [ [] for i in range(sparseColCount) ]
    for i,col in enumerate(data[1:]):
        for r,v in zip(rel,col):
            if v!='':
                try: complex(v)
                except ValueError: pass
                else:
                    unsparsed[2*i].append(r)
                    unsparsed[2*i+1].append(v)

    for i,col in enumerate(unsparsed):
        if i%2: # odd columns
            unsparsed[i] = dmap([col],[otherFunc])[0]
        else:
            unsparsed[i] = numpy.array(col)

    return numpy.array(unsparsed)

