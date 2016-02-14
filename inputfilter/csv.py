import numpy

def csv(infile):
    with open(infile) as f:
        return numpy.array( [ l.strip().split(',') for l in f ]).transpose()

def tsv(infile):
    with open(infile) as f:
        return numpy.array( [ l.split('\t') for l in f ] ).transpose()
