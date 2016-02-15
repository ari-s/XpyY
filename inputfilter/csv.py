import numpy,csv

def csv(infile,delimiter=','):
    with open(infile) as f:
        rv = [ l.strip().split(delimiter) for l in f ]
        width = max(map(len,rv))
        for l in rv:
            for i in range(len(l),width):
                l.append('')
    return numpy.array(rv).transpose()

def tsv(infile):
    return csv(infile,'\t')
