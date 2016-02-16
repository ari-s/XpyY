import numpy,csv

def csv(infile,delimiter=','):
    '''reads csv with arbitrary delimiter, returns numpy array of strings'''
    with open(infile) as f:
        rv = [ l.strip().split(delimiter) for l in f
                if l.strip()                            # no empty lines
                and not l.startswith('#')               # no comments
            ]
        width = max(map(len,rv))                        # make array rectangular
        for l in rv:
            for i in range(len(l),width):
                l.append('')
    return numpy.array(rv).transpose()

def tsv(infile):
    return csv(infile,'\t')
