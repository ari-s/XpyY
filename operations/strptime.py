import time,numpy,datetime,functools

dateStr = '%Y-%m-%d-%H:%M'
def strptime(data,dateStr=dateStr,mul=1):
    first = datetime.datetime.strptime(data[0],dateStr)
    return numpy.array([ (datetime.datetime.strptime(i,dateStr) - first).total_seconds() for i in data ],dtype=float)*mul

def strptime2(dateStr=dateStr,mul=1):
    return functools.partial(strptime,dateStr=dateStr,mul=mul)
